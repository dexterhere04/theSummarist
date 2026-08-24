"""Processing pipeline orchestration (backend.md §4).

Executed by the arq worker (``app.workers.worker``); each call owns its own
DB session because it runs outside the request lifecycle.

    upload/from-url → [uploaded] → [extracting] → [understanding]
                    → [preparing] → [ready]
"""
from __future__ import annotations

import logging

from sqlalchemy import delete, select

from app.core.errors import APIError
from app.database import SessionLocal
from app.models import Document, ExtractedText, Job, Summary, UserSettings
from app.models.enums import (
    Category,
    DetailLevel,
    DocSource,
    DocStatus,
    JobStage,
    JobStatus,
    JobType,
    SummaryFormat,
    SummaryStatus,
)
from app.services import extraction, summarizer
from app.services.chunking import flatten_body
from app.services.storage import storage

logger = logging.getLogger(__name__)


async def _advance(
    db, job: Job, stage: JobStage, progress: int, doc_status: DocStatus | None = None
) -> None:
    job.stage = stage
    job.progress = progress
    from app.models.enums import PIPELINE_STAGES

    job.stage_index = PIPELINE_STAGES.index(stage)
    if doc_status is not None:
        job_stage_doc = await db.get(Document, job.document_id)
        if job_stage_doc is not None:
            job_stage_doc.status = doc_status
    await db.commit()


async def _fail(db, job: Job, message: str) -> None:
    code = "EXTRACTION_FAILED" if job.type == JobType.extract else "UPSTREAM_ERROR"
    job.status = JobStatus.failed
    job.error = {"code": code, "message": message}
    if job.document_id is not None:
        doc = await db.get(Document, job.document_id)
        if doc is not None and doc.status != DocStatus.ready:
            doc.status = DocStatus.failed
    if job.summary_id is not None:
        summary = await db.get(Summary, job.summary_id)
        if summary is not None:
            summary.status = SummaryStatus.failed
    await db.commit()


def _default_params(default_length, default_style) -> dict:
    return {
        "format": SummaryFormat.bullets.value,
        "detail_level": DetailLevel.concise.value,
        "include_key_points": True,
        "include_quotes": False,
        "length": getattr(default_length, "value", str(default_length)),
        "style": getattr(default_style, "value", str(default_style)),
    }


async def run_extract_job(db, job: Job) -> None:
    doc = await db.get(Document, job.document_id) if job.document_id else None
    if doc is None:
        job.status = JobStatus.failed
        job.error = {"code": "NOT_FOUND", "message": "Document missing"}
        await db.commit()
        return

    # [extracting] — parse/OCR the source into ExtractedText.
    await _advance(db, job, JobStage.extracting, 25, DocStatus.extracting)
    try:
        if doc.source == DocSource.url and doc.source_url:
            result = await extraction.extract_from_url(doc.source_url)
        else:
            data = await storage.get(doc.storage_key or "")
            result = await extraction.extract_from_file(doc, data)
    except APIError as exc:
        await _fail(db, job, exc.message)
        return
    except Exception as exc:
        await _fail(db, job, f"Extraction failed: {exc}")
        return

    await db.execute(delete(ExtractedText).where(ExtractedText.document_id == doc.id))
    db.add(
        ExtractedText(
            document_id=doc.id, title=result["title"], body=result["body"]
        )
    )
    doc.pages = result["pages"]
    doc.words = result["words"]
    doc.language = result["language"]
    doc.ocr_method = result["ocr_method"]
    await db.commit()

    # [understanding] — semantic analysis / sectioning pass.
    await _advance(db, job, JobStage.understanding, 60, DocStatus.understanding)

    # [preparing] — LLM summarization with user defaults (when requested).
    run_summary = bool((job.payload or {}).get("run_summary", True))
    if run_summary:
        await _advance(db, job, JobStage.preparing, 85, DocStatus.preparing)

        settings_row = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == doc.user_id)
        )
        params = _default_params(
            settings_row.default_length if settings_row else "Medium",
            settings_row.default_style if settings_row else "executive",
        )
        flat_text = _flatten_body(result["body"])
        content = await summarizer.summarize_text(
            flat_text,
            length=params["length"],
            style=params["style"],
            fmt=params["format"],
            detail_level=params["detail_level"],
            include_key_points=params["include_key_points"],
            include_quotes=params["include_quotes"],
            blocks=flatten_body(result["body"]),
        )
        title = result.get("title") or doc.file_name
        summary = Summary(
            id=f"sum_{job.id.split('_', 1)[1]}",
            document_id=doc.id,
            user_id=doc.user_id,
            title=title,
            source=doc.file_name,
            format=doc.format,
            excerpt=content["excerpt"],
            length=params["length"],
            style=params["style"],
            category=_safe_category(content.get("category")),
            pages=doc.pages,
            words=doc.words,
            tldr=content["tldr"],
            takeaways=content["takeaways"],
            sections=content["sections"],
            highlight=content["highlight"],
            favorite=False,
            status=SummaryStatus.ready,
            params={
                k: params[k]
                for k in ("format", "detail_level", "include_key_points", "include_quotes")
            },
            job_id=job.id,
        )
        db.add(summary)
        await db.flush()
        job.summary_id = summary.id

    doc.status = DocStatus.ready
    job.status = JobStatus.succeeded
    job.stage = JobStage.preparing
    job.progress = 100
    await db.commit()


async def run_summarize_job(db, job: Job) -> None:
    summary = await db.get(Summary, job.summary_id) if job.summary_id else None
    if summary is None:
        job.status = JobStatus.failed
        job.error = {"code": "NOT_FOUND", "message": "Summary missing"}
        await db.commit()
        return

    et = await db.get(ExtractedText, summary.document_id)
    if et is None:
        await _fail(db, job, "Extracted text missing")
        return

    job.stage = JobStage.understanding
    job.stage_index = 2
    job.progress = 40
    await db.commit()

    params = summary.params or {}
    text = _flatten_body(et.body)
    content = await summarizer.summarize_text(
        text,
        length=getattr(summary.length, "value", str(summary.length)),
        style=getattr(summary.style, "value", str(summary.style)),
        fmt=params.get("format", "bullets"),
        detail_level=params.get("detail_level", "concise"),
        include_key_points=bool(params.get("include_key_points", True)),
        include_quotes=bool(params.get("include_quotes", False)),
        blocks=flatten_body(et.body),
    )

    job.stage = JobStage.preparing
    job.stage_index = 3
    job.progress = 90
    await db.commit()

    summary.tldr = content["tldr"]
    summary.excerpt = content["excerpt"]
    summary.takeaways = content["takeaways"]
    summary.sections = content["sections"]
    summary.highlight = content["highlight"]
    summary.category = _safe_category(content.get("category"))
    summary.status = SummaryStatus.ready

    job.status = JobStatus.succeeded
    job.progress = 100
    await db.commit()


def _flatten_body(body: list[dict]) -> str:
    parts: list[str] = []
    for section in body or []:
        heading = section.get("heading")
        if heading:
            parts.append(str(heading))
        for paragraph in section.get("paragraphs") or []:
            parts.append(str(paragraph))
        for bullet in section.get("bullets") or []:
            parts.append(f"- {bullet}")
    return "\n\n".join(parts)


def _safe_category(value) -> Category:
    try:
        return Category(str(value))
    except ValueError:
        return Category.Research


async def run_job(job_id: str) -> None:
    """Entry point invoked by the queue worker."""
    async with SessionLocal() as db:
        job = await db.get(Job, job_id)
        if job is None:
            logger.warning("Job %s not found", job_id)
            return
        if job.status in (JobStatus.succeeded, JobStatus.cancelled):
            return
        if job.status == JobStatus.failed:
            pass  # allow retry when re-enqueued

        job.status = JobStatus.running
        await db.commit()

        try:
            if job.type == JobType.extract:
                await run_extract_job(db, job)
            else:
                await run_summarize_job(db, job)
        except Exception as exc:
            await db.rollback()
            job = await db.get(Job, job_id)
            if job is not None:
                await _fail(db, job, str(exc))
            logger.exception("Job %s failed", job_id)
