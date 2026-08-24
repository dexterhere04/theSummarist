"""Pydantic schemas — summaries, share, TTS, meta."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.ids import relative_date
from app.models.enums import (
    STYLE_KIND_MAP,
    Category,
    DetailLevel,
    DocFormat,
    SummaryFormat,
    SummaryLength,
    SummaryStatus,
    SummaryStyle,
)
from app.models.summary import Summary


class Takeaway(BaseModel):
    title: str
    body: str


class SummarySection(BaseModel):
    heading: str
    body: str


class SummaryParams(BaseModel):
    format: SummaryFormat
    detail_level: DetailLevel
    include_key_points: bool
    include_quotes: bool


class SummaryCreateIn(BaseModel):
    document_id: str
    length: SummaryLength
    style: SummaryStyle
    format: SummaryFormat
    detail_level: DetailLevel
    include_key_points: bool = True
    include_quotes: bool = False


class SummaryRegenerateIn(BaseModel):
    length: SummaryLength | None = None
    style: SummaryStyle | None = None
    format: SummaryFormat | None = None
    detail_level: DetailLevel | None = None
    include_key_points: bool | None = None
    include_quotes: bool | None = None


class SummaryOut(BaseModel):
    id: str
    document_id: str
    user_id: str
    title: str
    source: str
    format: DocFormat
    excerpt: str
    date: str
    length: SummaryLength
    style: SummaryStyle
    kind: str
    category: Category
    pages: int | None
    words: int | None
    tldr: str
    takeaways: list[Takeaway]
    sections: list[SummarySection]
    highlight: str | None
    favorite: bool
    status: SummaryStatus
    params: SummaryParams
    created_at: datetime

    @classmethod
    def from_model(cls, s: Summary) -> SummaryOut:
        return cls(
            id=s.id,
            document_id=s.document_id,
            user_id=s.user_id,
            title=s.title,
            source=s.source,
            format=s.format,
            excerpt=s.excerpt,
            date=relative_date(s.created_at),
            length=s.length,
            style=s.style,
            kind=STYLE_KIND_MAP.get(s.style.value, s.style.value),
            category=s.category,
            pages=s.pages,
            words=s.words,
            tldr=s.tldr,
            takeaways=s.takeaways or [],
            sections=s.sections or [],
            highlight=s.highlight,
            favorite=s.favorite,
            status=s.status,
            params=s.params,
            created_at=s.created_at,
        )


class FavoriteResponse(BaseModel):
    favorite: bool


class ShareResponse(BaseModel):
    share_url: str
    token: str
    expires_at: datetime | None


class AudioResponse(BaseModel):
    audio_url: str
    duration_seconds: int
    voice: str


class AudioStatusResponse(BaseModel):
    status: str
    audio_url: str | None = None
    duration_seconds: int | None = None


class AudioGeneratingResponse(BaseModel):
    status: str = "generating"
    job_id: str


class CategoriesResponse(BaseModel):
    categories: list[str]


class StyleOption(BaseModel):
    value: str
    label: str
    description: str


class MetaOptionsResponse(BaseModel):
    lengths: list[str]
    styles: list[StyleOption]
    formats: list[str]
    detail_levels: list[str]
