"""Document and extracted-text models."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import DocFormat, DocSource, DocStatus


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    format: Mapped[DocFormat] = mapped_column(
        Enum(DocFormat, native_enum=False, length=8), nullable=False
    )
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[DocSource] = mapped_column(
        Enum(DocSource, native_enum=False, length=8),
        default=DocSource.upload,
        nullable=False,
    )
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[DocStatus] = mapped_column(
        Enum(DocStatus, native_enum=False, length=16),
        default=DocStatus.uploaded,
        nullable=False,
    )
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    words: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ocr_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Storage key of the original file (object key / local path).
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    extracted_text: Mapped[ExtractedText] = relationship(
        back_populates="document", uselist=False, cascade="all, delete-orphan"
    )


class ExtractedText(Base):
    __tablename__ = "extracted_texts"

    document_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    title: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    # body: list[{"heading", "paragraphs": [...], "bullets": [...]}]
    body: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    document: Mapped[Document] = relationship(back_populates="extracted_text")
