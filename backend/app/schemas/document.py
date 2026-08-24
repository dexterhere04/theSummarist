"""Pydantic schemas — documents & extracted text."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.document import Document, ExtractedText
from app.models.enums import DocFormat, DocSource, DocStatus


class DocumentOut(BaseModel):
    id: str
    user_id: str
    file_name: str
    format: DocFormat
    mime_type: str
    size_bytes: int
    source: DocSource
    source_url: str | None
    status: DocStatus
    pages: int | None
    words: int | None
    language: str | None
    ocr_method: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, d: Document) -> DocumentOut:
        return cls(
            id=d.id,
            user_id=d.user_id,
            file_name=d.file_name,
            format=d.format,
            mime_type=d.mime_type,
            size_bytes=d.size_bytes,
            source=d.source,
            source_url=d.source_url,
            status=d.status,
            pages=d.pages,
            words=d.words,
            language=d.language,
            ocr_method=d.ocr_method,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )


class ExtractedSection(BaseModel):
    heading: str
    paragraphs: list[str]
    bullets: list[str] | None = None


class ExtractedTextOut(BaseModel):
    document_id: str
    title: str
    file_name: str
    format: DocFormat
    pages: int | None
    words: int | None
    language: str | None
    ocr_method: str | None
    body: list[ExtractedSection]

    @classmethod
    def from_models(cls, d: Document, et: ExtractedText) -> ExtractedTextOut:
        return cls(
            document_id=d.id,
            title=et.title or d.file_name,
            file_name=d.file_name,
            format=d.format,
            pages=d.pages,
            words=d.words,
            language=d.language,
            ocr_method=d.ocr_method,
            body=et.body,
        )


class FromURLIn(BaseModel):
    url: str


class SearchMatch(BaseModel):
    section_heading: str
    paragraph_index: int
    snippet: str
    start: int
    end: int


class SearchResponse(BaseModel):
    matches: list[SearchMatch]
    total: int
