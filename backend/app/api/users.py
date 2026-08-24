"""Current-user profile and settings endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import ConflictError
from app.database import get_db
from app.models import User, UserSettings
from app.schemas.user import (
    UpdateMeIn,
    UserOut,
    UserSettingsOut,
    UserSettingsUpdateIn,
)

router = APIRouter(prefix="/me", tags=["users"])


async def _load_or_create_settings(user_id: str, db: AsyncSession) -> UserSettings:
    settings_obj = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    if settings_obj is None:
        settings_obj = UserSettings(user_id=user_id)
        db.add(settings_obj)
        await db.commit()
        await db.refresh(settings_obj)
    return settings_obj


@router.get("", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.from_model(user)


@router.patch("", response_model=UserOut)
async def update_me(
    body: UpdateMeIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    if body.name is not None:
        user.name = body.name

    if body.email is not None and body.email != user.email:
        existing = await db.scalar(
            select(User).where(User.email == body.email, User.id != user.id)
        )
        if existing is not None:
            raise ConflictError("Email already in use")
        user.email = body.email

    await db.commit()
    await db.refresh(user)
    return UserOut.from_model(user)


@router.get("/settings", response_model=UserSettingsOut)
async def get_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsOut:
    settings_obj = await _load_or_create_settings(user.id, db)
    return UserSettingsOut.from_model(settings_obj)


@router.patch("/settings", response_model=UserSettingsOut)
async def update_settings(
    body: UserSettingsUpdateIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsOut:
    settings_obj = await _load_or_create_settings(user.id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(settings_obj, field, value)
    await db.commit()
    await db.refresh(settings_obj)
    return UserSettingsOut.from_model(settings_obj)
