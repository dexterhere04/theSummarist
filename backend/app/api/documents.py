"""Document upload, retrieval, and extracted-text endpoints."""
from __future__ import annotations

import urllib.parse

from fastapi import APIRouter, Depends, File, Form, Header, Query, Response, UploadFile, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_owned_document
from app.config import settings
from app.core.errors import (
    ConflictError,
    FileTooLargeError,
    InvalidURLError,
    NotFoundError,
    UnsupportedTypeError,
)
from app.core.ids import gen_id, utcnow
from app.core.mime import format_for_mime, is_allowed_mime
from app.core.pagination import build_page, clamp_page, clamp_per_page, offset
from app.database import get_db
from app.models import Document, ExtractedText, Job, Summary
from app.models.enums import DocFormat, DocSource, DocStatus, JobStage, JobStatus, JobType
from app.schemas.document import (
    DocumentOut,
    ExtractedTextOut,
    FromURLIn,
    SearchMatch,
    SearchResponse,
)
from app.schemas.job import JobOut
from app.services.queue import enqueue_job
from app.services.storage import storage

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    run_summary: bool = Form(True),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise FileTooLargeError("File exceeds 50 MB limit")

    mime = (file.content_type or "").lower()
    if not is_allowed_mime(mime):
        raise UnsupportedTypeError("Unsupported file type")
    doc_format = format_for_mime(mime)

    doc = Document(
        id=gen_id("doc"),
        user_id=user.id,
        file_name=file.filename or "document",
        format=doc_format,
        mime_type=mime,
        size_bytes=len(data),
        source=DocSource.upload,
        status=DocStatus.uploaded,
    )

    storage_key = f"{user.id}/{doc.id}/{file.filename or 'document'}"
    await storage.put(storage_key, data, mime)
    doc.storage_key = storage_key

    job = Job(
        id=gen_id("job"),
        document_id=doc.id,
        user_id=user.id,
        type=JobType.extract,
        status=JobStatus.pending,
        stage=JobStage.uploaded,
        stage_index=0,
        total_stages=4,
        payload={"run_summary": run_summary},
    )

    db.add(doc)
    db.add(job)
    await db.commit()
    await db.refresh(doc)
    await db.refresh(job)

    try:
        await enqueue_job(job.id)
    except Exception:
        pass

    return {"document": DocumentOut.from_model(doc), "job": JobOut.from_model(job)}


@router.post("/from-url", status_code=status.HTTP_202_ACCEPTED)
async def from_url(
    body: FromURLIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    parsed = urllib.parse.urlparse(body.url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise InvalidURLError("Invalid URL")

    file_name = f"{parsed.hostname}{parsed.path}".strip("/") or "webpage"

    doc = Document(
        id=gen_id("doc"),
        user_id=user.id,
        file_name=file_name,
        format=DocFormat.WEB,
        mime_type="text/html",
        size_bytes=0,
        source=DocSource.url,
        source_url=body.url,
        status=DocStatus.uploaded,
    )

    job = Job(
        id=gen_id("job"),
        document_id=doc.id,
        user_id=user.id,
        type=JobType.extract,
        status=JobStatus.pending,
        stage=JobStage.uploaded,
        stage_index=0,
        total_stages=4,
        payload={"run_summary": True},
    )

    db.add(doc)
    db.add(job)
    await db.commit()
    await db.refresh(doc)
    await db.refresh(job)

    try:
        await enqueue_job(job.id)
    except Exception:
        pass

    return {"document": DocumentOut.from_model(doc), "job": JobOut.from_model(job)}


@router.get("")
async def list_documents(
    page: int = 1,
    per_page: int = 20,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    page = clamp_page(page)
    per_page = clamp_per_page(per_page)

    filters = [Document.user_id == user.id, Document.deleted_at.is_(None)]
    if q:
        filters.append(Document.file_name.ilike(f"%{q}%"))

    total = await db.scalar(
        select(func.count()).select_from(Document).where(*filters)
    )

    result = await db.scalars(
        select(Document)
        .where(*filters)
        .order_by(Document.created_at.desc())
        .offset(offset(page, per_page))
        .limit(per_page)
    )
    docs = result.all()

    items = [DocumentOut.from_model(d).model_dump(mode="json") for d in docs]
    return build_page(items, page, per_page, total)


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    return DocumentOut.from_model(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    doc.deleted_at = utcnow()
    await db.execute(
        update(Summary)
        .where(Summary.document_id == doc.id)
        .values(deleted_at=utcnow())
    )
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{document_id}/status", response_model=JobOut)
async def get_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    job = await db.scalar(
        select(Job)
        .where(Job.document_id == doc.id)
        .order_by(Job.created_at.desc())
        .limit(1)
    )
    if job is None:
        raise NotFoundError("No job found")
    return JobOut.from_model(job)


@router.get("/{document_id}/extracted-text", response_model=ExtractedTextOut)
async def get_extracted_text(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    et = await db.get(ExtractedText, doc.id)
    if doc.status != DocStatus.ready or et is None:
        raise ConflictError("Extraction not complete")
    return ExtractedTextOut.from_models(doc, et)


@router.get("/{document_id}/download")
async def download(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    if not doc.storage_key:
        raise NotFoundError("File not found")
    data = await storage.get(doc.storage_key)
    return StreamingResponse(
        iter([data]),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'},
    )


@router.get("/{document_id}/export.txt")
async def export_txt(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    et = await db.get(ExtractedText, doc.id)
    if doc.status != DocStatus.ready or et is None:
        raise ConflictError("Extraction not complete")

    parts: list[str] = []
    for section in et.body:
        heading = section.get("heading")
        if heading:
            parts.append(heading)
        for paragraph in section.get("paragraphs") or []:
            if paragraph:
                parts.append(paragraph)
        for bullet in section.get("bullets") or []:
            if bullet:
                parts.append(bullet)

    flattened = "\n\n".join(parts)
    return PlainTextResponse(
        flattened,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{doc.id}.txt"'},
    )


def _occurrences(text: str, needle: str) -> list[int]:
    lower = text.lower()
    positions: list[int] = []
    start = 0
    while True:
        idx = lower.find(needle, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


@router.get("/{document_id}/search", response_model=SearchResponse)
async def search(
    document_id: str,
    q: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = await get_owned_document(document_id, user, db)
    et = await db.get(ExtractedText, doc.id)
    if doc.status != DocStatus.ready or et is None:
        raise ConflictError("Extraction not complete")

    q_lower = q.lower()
    matches: list[SearchMatch] = []
    cursor = 0

    for section in et.body:
        heading = section.get("heading") or ""
        paragraphs = section.get("paragraphs") or []
        bullets = section.get("bullets") or []

        cursor += len(heading) + (2 if heading else 0)

        for idx, paragraph in enumerate(paragraphs):
            base = cursor
            for pos in _occurrences(paragraph, q_lower):
                snippet = paragraph[max(0, pos - 30) : pos + len(q) + 30]
                matches.append(
                    SearchMatch(
                        section_heading=heading,
                        paragraph_index=idx,
                        snippet=snippet,
                        start=base + pos,
                        end=base + pos + len(q),
                    )
                )
            cursor += len(paragraph) + 2

        for bullet in bullets:
            base = cursor
            for pos in _occurrences(bullet, q_lower):
                snippet = bullet[max(0, pos - 30) : pos + len(q) + 30]
                matches.append(
                    SearchMatch(
                        section_heading=heading,
                        paragraph_index=-1,
                        snippet=snippet,
                        start=base + pos,
                        end=base + pos + len(q),
                    )
                )
            cursor += len(bullet) + 2

    return SearchResponse(matches=matches[:100], total=len(matches))
