"""Pydantic schemas — user & settings."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.ids import avatar_initials
from app.models.enums import SummaryLength, SummaryStyle
from app.models.user import User, UserSettings


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    avatar_initials: str
    plan: str
    created_at: datetime

    @classmethod
    def from_model(cls, u: User) -> UserOut:
        return cls(
            id=u.id,
            email=u.email,
            name=u.name,
            avatar_initials=avatar_initials(u.name),
            plan=u.plan,
            created_at=u.created_at,
        )


class UpdateMeIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=320)


class UserSettingsOut(BaseModel):
    default_length: SummaryLength
    default_style: SummaryStyle
    language: str
    tts_voice: str
    theme: str

    @classmethod
    def from_model(cls, s: UserSettings) -> UserSettingsOut:
        return cls(
            default_length=s.default_length,
            default_style=s.default_style,
            language=s.language,
            tts_voice=s.tts_voice,
            theme=s.theme,
        )


class UserSettingsUpdateIn(BaseModel):
    default_length: SummaryLength | None = None
    default_style: SummaryStyle | None = None
    language: str | None = None
    tts_voice: str | None = None
    theme: str | None = None
