"""Summary, share, download, and audio endpoints."""
from __future__ import annotations

import secrets
from datetime import timedelta
from io import BytesIO

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_owned_document, get_owned_summary
from app.config import settings
from app.core.errors import ConflictError, NotFoundError
from app.core.ids import as_utc, gen_id, utcnow
from app.core.pagination import build_page, clamp_page, clamp_per_page, offset
from app.database import get_db
from app.models import Job, ShareToken, Summary
from app.models.enums import (
    Category,
    DocFormat,
    DocStatus,
    JobStage,
    JobStatus,
    JobType,
    SummaryLength,
    SummaryStatus,
    SummaryStyle,
)
from app.schemas.job import JobOut
from app.schemas.summary import (
    AudioResponse,
    AudioStatusResponse,
    FavoriteResponse,
    ShareResponse,
    SummaryCreateIn,
    SummaryOut,
    SummaryRegenerateIn,
)
from app.services.queue import enqueue_job
from app.services.tts import generate_audio

router = APIRouter(prefix="/summaries", tags=["summaries"])
share_router = APIRouter(prefix="/share", tags=["share"])


def _render_markdown(s: Summary) -> str:
    lines: list[str] = [f"# {s.title}", ""]
    if s.tldr:
        lines += ["## TL;DR", "", s.tldr, ""]
    takeaways = s.takeaways or []
    if takeaways:
        lines += ["## Key Takeaways", ""]
        for t in takeaways:
            title = t.get("title") if isinstance(t, dict) else None
            body = t.get("body") if isinstance(t, dict) else None
            if title and body:
                lines.append(f"- **{title}**: {body}")
            elif title:
                lines.append(f"- **{title}**")
            elif body:
                lines.append(f"- {body}")
        lines.append("")
    sections = s.sections or []
    if sections:
        lines += ["## Detailed Analysis", ""]
        for sec in sections:
            heading = sec.get("heading") if isinstance(sec, dict) else None
            body = sec.get("body") if isinstance(sec, dict) else None
            if heading:
                lines += [f"### {heading}", ""]
            if body:
                lines += [body, ""]
    if s.highlight:
        lines += ["## Notable Quote", "", f"> {s.highlight}", ""]
    return "\n".join(lines)


def _render_plain_text(s: Summary) -> str:
    lines: list[str] = [s.title, ""]
    if s.tldr:
        lines += ["TL;DR", s.tldr, ""]
    takeaways = s.takeaways or []
    if takeaways:
        lines.append("Key Takeaways")
        for t in takeaways:
            title = t.get("title") if isinstance(t, dict) else None
            body = t.get("body") if isinstance(t, dict) else None
            if title and body:
                lines.append(f"- {title}: {body}")
            elif title:
                lines.append(f"- {title}")
            elif body:
                lines.append(f"- {body}")
        lines.append("")
    sections = s.sections or []
    if sections:
        lines.append("Detailed Analysis")
        for sec in sections:
            heading = sec.get("heading") if isinstance(sec, dict) else None
            body = sec.get("body") if isinstance(sec, dict) else None
            if heading:
                lines.append(str(heading))
            if body:
                lines.append(str(body))
        lines.append("")
    if s.highlight:
        lines += ["Notable Quote", f'"{s.highlight}"', ""]
    return "\n".join(lines)


def _audio_text(s: Summary) -> str:
    parts: list[str] = []
    if s.tldr:
        parts.append(s.tldr)
    for sec in s.sections or []:
        if isinstance(sec, dict):
            if sec.get("heading"):
                parts.append(str(sec["heading"]))
            if sec.get("body"):
                parts.append(str(sec["body"]))
    return "\n".join(parts)


def _build_pdf(text: str) -> bytes:
    escaped = (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\r", "")
    )
    content_lines: list[str] = ["BT", "/F1 12 Tf", "50 780 Td", "14 TL"]
    for line in escaped.split("\n"):
        content_lines.append(f"({line}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    content = "\n".join(content_lines)

    obj1 = "<< /Type /Catalog /Pages 2 0 R >>"
    obj2 = "<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    obj3 = (
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    )
    obj4 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    obj5 = f"<< /Length {len(content)} >>\nstream\n{content}\nendstream"
    objects = [obj1, obj2, obj3, obj4, obj5]

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode()
        out += obj.encode()
        out += b"\nendobj\n"

    xref_offset = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode()
    return bytes(out)


@router.post("", status_code=202)
async def generate_summary(
    body: SummaryCreateIn,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc = await get_owned_document(body.document_id, user, db)
    if doc.status != DocStatus.ready:
        raise ConflictError("Document is not ready")

    params = {
        "format": body.format.value,
        "detail_level": body.detail_level.value,
        "include_key_points": body.include_key_points,
        "include_quotes": body.include_quotes,
    }
    from app.models import ExtractedText

    et = await db.get(ExtractedText, doc.id)
    title = et.title if et and et.title else doc.file_name

    summary = Summary(
        id=gen_id("sum"),
        document_id=doc.id,
        user_id=user.id,
        title=title,
        source=doc.file_name,
        format=doc.format,
        excerpt="",
        length=body.length,
        style=body.style,
        category=Category.Research,
        pages=doc.pages,
        words=doc.words,
        tldr="",
        takeaways=[],
        sections=[],
        highlight=None,
        favorite=False,
        status=SummaryStatus.generating,
        params=params,
    )
    db.add(summary)

    job = Job(
        id=gen_id("job"),
        document_id=doc.id,
        user_id=user.id,
        summary_id=summary.id,
        type=JobType.summarize,
        status=JobStatus.pending,
        stage=JobStage.understanding,
        stage_index=2,
        total_stages=4,
    )
    db.add(job)
    summary.job_id = job.id

    await db.commit()
    await db.refresh(summary)
    await db.refresh(job)

    try:
        await enqueue_job(job.id)
    except Exception:
        pass

    return {"summary": SummaryOut.from_model(summary), "job": JobOut.from_model(job)}


@router.get("")
async def list_summaries(
    tab: str = "all",
    q: str | None = None,
    category: str | None = None,
    format: str | None = None,
    length: str | None = None,
    style: str | None = None,
    sort: str = "created_at",
    page: int = 1,
    per_page: int = 20,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    page = clamp_page(page)
    per_page = clamp_per_page(per_page)

    conditions: list = [
        Summary.user_id == user.id,
        Summary.deleted_at.is_(None),
    ]
    if tab == "favorites":
        conditions.append(Summary.favorite.is_(True))
    if q:
        like = f"%{q}%"
        conditions.append(
            or_(
                Summary.title.ilike(like),
                Summary.excerpt.ilike(like),
                Summary.source.ilike(like),
            )
        )
    if category:
        try:
            conditions.append(Summary.category == Category(category))
        except ValueError:
            pass
    if format:
        conditions.append(Summary.format == DocFormat(format))
    if length:
        conditions.append(Summary.length == SummaryLength(length))
    if style:
        conditions.append(Summary.style == SummaryStyle(style))

    order = Summary.title.asc() if sort == "title" else Summary.created_at.desc()

    total = await db.scalar(
        select(func.count()).select_from(Summary).where(*conditions)
    )
    rows = (
        await db.scalars(
            select(Summary)
            .where(*conditions)
            .order_by(order)
            .offset(offset(page, per_page))
            .limit(per_page)
        )
    ).all()

    items = [SummaryOut.from_model(s).model_dump(mode="json") for s in rows]
    return build_page(items, page, per_page, total or 0)


@router.get("/{summary_id}", response_model=SummaryOut)
async def get_summary(
    summary_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SummaryOut:
    s = await get_owned_summary(summary_id, user, db)
    return SummaryOut.from_model(s)


@router.post("/{summary_id}/regenerate", status_code=202)
async def regenerate_summary(
    summary_id: str,
    body: SummaryRegenerateIn,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    s = await get_owned_summary(summary_id, user, db)

    params = dict(s.params or {})
    if body.format is not None:
        params["format"] = body.format.value
    if body.detail_level is not None:
        params["detail_level"] = body.detail_level.value
    if body.include_key_points is not None:
        params["include_key_points"] = body.include_key_points
    if body.include_quotes is not None:
        params["include_quotes"] = body.include_quotes
    s.params = params

    if body.length is not None:
        s.length = body.length
    if body.style is not None:
        s.style = body.style

    s.status = SummaryStatus.generating

    job = Job(
        id=gen_id("job"),
        document_id=s.document_id,
        user_id=s.user_id,
        summary_id=s.id,
        type=JobType.summarize,
        status=JobStatus.pending,
        stage=JobStage.understanding,
        stage_index=2,
        total_stages=4,
    )
    db.add(job)
    s.job_id = job.id

    await db.commit()
    await db.refresh(s)
    await db.refresh(job)

    try:
        await enqueue_job(job.id)
    except Exception:
        pass

    return {"summary": SummaryOut.from_model(s), "job": JobOut.from_model(job)}


@router.delete("/{summary_id}", status_code=204)
async def delete_summary(
    summary_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    s = await get_owned_summary(summary_id, user, db)
    s.deleted_at = utcnow()
    await db.commit()
    return Response(status_code=204)


@router.post("/{summary_id}/favorite", response_model=FavoriteResponse)
async def toggle_favorite(
    summary_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FavoriteResponse:
    s = await get_owned_summary(summary_id, user, db)
    s.favorite = not s.favorite
    await db.commit()
    return FavoriteResponse(favorite=s.favorite)


@router.get("/{summary_id}/download")
async def download_summary(
    summary_id: str,
    format: str = Query("markdown"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = await get_owned_summary(summary_id, user, db)

    if format == "pdf":
        try:
            data = _build_pdf(_render_plain_text(s))
        except Exception:
            md = _render_markdown(s)
            return PlainTextResponse(
                md,
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="{s.id}.md"'},
            )
        return StreamingResponse(
            BytesIO(data),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{s.id}.pdf"'},
        )

    if format == "txt":
        return PlainTextResponse(
            _render_plain_text(s),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{s.id}.txt"'},
        )

    return PlainTextResponse(
        _render_markdown(s),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{s.id}.md"'},
    )


@router.post("/{summary_id}/share", response_model=ShareResponse)
async def share_summary(
    summary_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShareResponse:
    s = await get_owned_summary(summary_id, user, db)

    token = secrets.token_urlsafe(24)
    expires_at = utcnow() + timedelta(days=7)
    share_token = ShareToken(token=token, summary_id=s.id, expires_at=expires_at)
    db.add(share_token)
    await db.commit()

    share_url = f"{settings.public_base_url}/share/{token}"
    return ShareResponse(share_url=share_url, token=token, expires_at=expires_at)


@router.get("/{summary_id}/audio", response_model=AudioResponse)
async def get_audio(
    summary_id: str,
    voice: str = Query("default"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AudioResponse:
    s = await get_owned_summary(summary_id, user, db)
    audio = await generate_audio(_audio_text(s), voice)
    return AudioResponse(
        audio_url=audio["audio_url"],
        duration_seconds=audio["duration_seconds"],
        voice=audio["voice"],
    )


@router.get("/{summary_id}/audio/status", response_model=AudioStatusResponse)
async def get_audio_status(
    summary_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AudioStatusResponse:
    s = await get_owned_summary(summary_id, user, db)
    audio = await generate_audio(_audio_text(s), "default")
    return AudioStatusResponse(
        status="ready",
        audio_url=audio["audio_url"],
        duration_seconds=audio["duration_seconds"],
    )


@share_router.get("/{token}", response_model=SummaryOut)
async def get_shared_summary(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> SummaryOut:
    st = await db.get(ShareToken, token)
    if st is None:
        raise NotFoundError("Share link not found")
    if st.expires_at is not None and as_utc(st.expires_at) < utcnow():
        raise NotFoundError("Share link expired")

    summary = await db.get(Summary, st.summary_id)
    if summary is None or summary.deleted_at is not None:
        raise NotFoundError("Share link not found")

    return SummaryOut.from_model(summary)
