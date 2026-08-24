"""Shared FastAPI dependencies (auth + resource ownership)."""
from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, UnauthenticatedError
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.database import get_db
from app.models.document import Document
from app.models.summary import Summary
from app.models.user import User


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthenticatedError("Missing bearer token.")
    payload = decode_token(authorization.removeprefix("Bearer "), TOKEN_TYPE_ACCESS)
    user = await db.get(User, payload["sub"])
    if user is None:
        raise UnauthenticatedError("User no longer exists.")
    return user


async def get_owned_document(
    document_id: str, user: User, db: AsyncSession
) -> Document:
    doc = await db.get(Document, document_id)
    if doc is None or doc.user_id != user.id or doc.deleted_at is not None:
        raise NotFoundError("Document not found.")
    return doc


async def get_owned_summary(summary_id: str, user: User, db: AsyncSession) -> Summary:
    summary = await db.get(Summary, summary_id)
    if summary is None or summary.user_id != user.id or summary.deleted_at is not None:
        raise NotFoundError("Summary not found.")
    return summary
