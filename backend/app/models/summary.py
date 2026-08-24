"""Summary and share-token models."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import (
    Category,
    DocFormat,
    SummaryLength,
    SummaryStatus,
    SummaryStyle,
)


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    format: Mapped[DocFormat] = mapped_column(
        Enum(DocFormat, native_enum=False, length=8), nullable=False
    )
    excerpt: Mapped[str] = mapped_column(String(2048), default="", nullable=False)
    length: Mapped[SummaryLength] = mapped_column(
        Enum(SummaryLength, native_enum=False, length=16), nullable=False
    )
    style: Mapped[SummaryStyle] = mapped_column(
        Enum(SummaryStyle, native_enum=False, length=24), nullable=False
    )
    category: Mapped[Category] = mapped_column(
        Enum(Category, native_enum=False, length=16), nullable=False
    )
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    words: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tldr: Mapped[str] = mapped_column(String(4096), default="", nullable=False)
    takeaways: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    sections: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    highlight: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[SummaryStatus] = mapped_column(
        Enum(SummaryStatus, native_enum=False, length=16),
        default=SummaryStatus.generating,
        nullable=False,
    )
    # params: {"format", "detail_level", "include_key_points", "include_quotes"}
    params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    # Last completed job id (for status polling / audio lookup).
    job_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ShareToken(Base):
    __tablename__ = "share_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    summary_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("summaries.id", ondelete="CASCADE"), index=True, nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
