"""Processing job model."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import JobStage, JobStatus, JobType


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )
    summary_id: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    type: Mapped[JobType] = mapped_column(
        Enum(JobType, native_enum=False, length=16), nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, length=16),
        default=JobStatus.pending,
        nullable=False,
    )
    stage: Mapped[JobStage] = mapped_column(
        Enum(JobStage, native_enum=False, length=16),
        default=JobStage.uploaded,
        nullable=False,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stage_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_stages: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    # Arbitrary job configuration, e.g. {"run_summary": true} for extract jobs.
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
