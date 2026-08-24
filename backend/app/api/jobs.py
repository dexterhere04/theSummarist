"""Job endpoints — status, SSE streaming, cancel, and meta options."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import NotFoundError
from app.database import SessionLocal, get_db
from app.models import Document, Job
from app.models.enums import DocStatus, JobStatus
from app.schemas.job import JobOut
from app.schemas.summary import CategoriesResponse, MetaOptionsResponse, StyleOption

router = APIRouter(prefix="/jobs", tags=["jobs"])
meta_router = APIRouter(tags=["meta"])


async def _get_owned_job(job_id: str, user, db: AsyncSession) -> Job:
    job = await db.get(Job, job_id)
    if job is None or job.user_id != user.id:
        raise NotFoundError("Job not found")
    return job


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobOut:
    job = await _get_owned_job(job_id, user, db)
    return JobOut.from_model(job)


@router.get("/{job_id}/stream")
async def stream(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> StreamingResponse:
    await _get_owned_job(job_id, user, db)

    async def event_stream():
        async with SessionLocal() as s:
            for _ in range(600):
                await asyncio.sleep(0.5)

                j = await s.get(Job, job_id)
                if j is None:
                    yield "event: error\n"
                    yield "data: " + json.dumps(
                        {"error": {"code": "JOB_NOT_FOUND", "message": "Job not found"}}
                    ) + "\n\n"
                    break

                yield "event: stage\n"
                yield "data: " + json.dumps(
                    {
                        "stage": j.stage.value,
                        "stage_index": j.stage_index,
                        "progress": j.progress,
                    }
                ) + "\n\n"

                if j.status == JobStatus.succeeded:
                    yield "event: complete\n"
                    yield "data: " + json.dumps(
                        {
                            "document_id": j.document_id,
                            "summary_id": j.summary_id,
                        }
                    ) + "\n\n"
                    break

                if j.status in (JobStatus.failed, JobStatus.cancelled):
                    yield "event: error\n"
                    yield "data: " + json.dumps(
                        {
                            "error": j.error
                            or {
                                "code": "JOB_FAILED",
                                "message": "Job did not complete",
                            }
                        }
                    ) + "\n\n"
                    break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/{job_id}/cancel")
async def cancel(
    job_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    job = await _get_owned_job(job_id, user, db)
    job.status = JobStatus.cancelled
    if job.document_id:
        doc = await db.get(Document, job.document_id)
        if doc is not None:
            doc.status = DocStatus.failed
    await db.commit()
    return {"status": "cancelled"}


@router.post("/{job_id}/background")
async def background(
    job_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    job = await _get_owned_job(job_id, user, db)
    if job.status == JobStatus.pending:
        job.status = JobStatus.running
    await db.commit()
    return {"status": "running"}


@meta_router.get("/categories", response_model=CategoriesResponse)
async def categories() -> CategoriesResponse:
    return CategoriesResponse(categories=["Research", "Finance", "Tech", "Internal"])


@meta_router.get("/meta/options", response_model=MetaOptionsResponse)
async def meta_options() -> MetaOptionsResponse:
    return MetaOptionsResponse(
        lengths=["Short", "Medium", "Long"],
        styles=[
            StyleOption(
                value="executive",
                label="Executive Summary",
                description="High-level overview focusing on main conclusions and decisions.",
            ),
            StyleOption(
                value="key_points",
                label="Key Points",
                description="Bullet-point list extracting the most critical facts.",
            ),
            StyleOption(
                value="detailed",
                label="Detailed Summary",
                description="Comprehensive breakdown preserving structural flow.",
            ),
            StyleOption(
                value="study_notes",
                label="Study Notes",
                description="Optimized for learning and memorization.",
            ),
            StyleOption(
                value="action_items",
                label="Action Items",
                description="Extracts tasks, deadlines, and responsibilities.",
            ),
        ],
        formats=["PDF", "DOC", "DOCX", "PPTX", "TXT", "WEB"],
        detail_levels=["concise", "medium", "detailed"],
    )
