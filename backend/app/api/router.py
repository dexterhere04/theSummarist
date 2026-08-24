"""Aggregated /api/v1 router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api import auth, documents, jobs, summaries, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(summaries.router)
api_router.include_router(summaries.share_router)
api_router.include_router(jobs.router)
api_router.include_router(jobs.meta_router)
