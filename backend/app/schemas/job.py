"""Pydantic schemas — jobs."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import JobStage, JobStatus, JobType
from app.models.job import Job


class JobOut(BaseModel):
    id: str
    document_id: str | None
    user_id: str | None = None
    summary_id: str | None = None
    type: JobType
    status: JobStatus
    stage: JobStage
    progress: int
    stage_index: int
    total_stages: int
    error: dict[str, Any] | None
    created_at: datetime

    @classmethod
    def from_model(cls, j: Job) -> JobOut:
        return cls(
            id=j.id,
            document_id=j.document_id,
            user_id=j.user_id,
            summary_id=j.summary_id,
            type=j.type,
            status=j.status,
            stage=j.stage,
            progress=j.progress,
            stage_index=j.stage_index,
            total_stages=j.total_stages,
            error=j.error,
            created_at=j.created_at,
        )
