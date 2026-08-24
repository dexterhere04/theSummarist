"""Authentication endpoints — register, login, refresh, logout."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, UnauthenticatedError
from app.core.ids import gen_id
from app.core.security import (
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import User, UserSettings
from app.schemas.auth import (
    LoginIn,
    LogoutIn,
    RefreshIn,
    RegisterIn,
    TokenPair,
    TokenResponse,
)
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise ConflictError("Email already registered")

    user = User(
        id=gen_id("usr"),
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
    )
    settings_obj = UserSettings(user_id=user.id)
    db.add(user)
    db.add(settings_obj)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        user=UserOut.from_model(user),
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise UnauthenticatedError("Invalid credentials")

    return TokenResponse(
        user=UserOut.from_model(user),
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, db: AsyncSession = Depends(get_db)) -> TokenPair:
    payload = decode_token(body.refresh_token, TOKEN_TYPE_REFRESH)
    user = await db.get(User, payload["sub"])
    if user is None:
        raise UnauthenticatedError("User not found")

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutIn) -> Response:
    decode_token(body.refresh_token, TOKEN_TYPE_REFRESH)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
