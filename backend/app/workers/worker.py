"""arq worker entry point.

Run with: uv run arq app.workers.worker.WorkerSettings
"""
from __future__ import annotations

from typing import ClassVar

from arq.connections import RedisSettings

from app.services.pipeline import run_job as _run_job
from app.services.queue import redis_settings


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


async def run_job(ctx: dict, job_id: str) -> None:
    await _run_job(job_id)


class WorkerSettings:
    # arq requires these as plain class attributes; they are read, not mutated.
    functions: ClassVar[list] = [run_job]
    redis_settings: ClassVar[RedisSettings] = redis_settings()
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 4
    job_timeout = 600
