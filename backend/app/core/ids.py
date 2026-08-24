"""ID and datetime helpers."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta


def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:20]}"


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_utc(dt: datetime) -> datetime:
    """Normalize a possibly-naive datetime (e.g. from SQLite) to aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def relative_date(dt: datetime) -> str:
    """Pre-format a display date string per backend.md §2.4 examples."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    now = utcnow()
    delta = now - dt
    if delta < timedelta(hours=24) and dt.date() == now.date():
        return f"Today, {dt.strftime('%-I:%M %p').lstrip('0')}"
    yesterday = now.date() - timedelta(days=1)
    if dt.date() == yesterday:
        return "Yesterday"
    if dt.year == now.year:
        return dt.strftime("%b %-d, %Y")
    return dt.strftime("%b %-d, %Y")


def avatar_initials(name: str) -> str:
    name = name.strip()
    if not name:
        return "?"
    return name[0].upper()
