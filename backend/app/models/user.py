"""User and user-settings models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import SummaryLength, SummaryStyle


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(32), default="free", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    settings: Mapped[UserSettings] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    default_length: Mapped[SummaryLength] = mapped_column(
        Enum(SummaryLength, native_enum=False, length=16),
        default=SummaryLength.Medium,
        nullable=False,
    )
    default_style: Mapped[SummaryStyle] = mapped_column(
        Enum(SummaryStyle, native_enum=False, length=24),
        default=SummaryStyle.executive,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(String(16), default="en-US", nullable=False)
    tts_voice: Mapped[str] = mapped_column(String(64), default="default", nullable=False)
    theme: Mapped[str] = mapped_column(String(16), default="light", nullable=False)

    user: Mapped[User] = relationship(back_populates="settings")
