"""Pydantic schemas — authentication."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class RegisterIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
