"""Redis-backed job queue via arq.

The single task name ``run_job`` is consumed by the worker in
``app.workers.worker`` and dispatched to ``app.services.pipeline.run_job``.
"""
from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.config import settings

QUEUE_TASK = "run_job"


def redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(settings.redis_url)


async def enqueue_job(job_id: str) -> None:
    redis: ArqRedis = await create_pool(redis_settings())
    try:
        await redis.enqueue_job(QUEUE_TASK, job_id)
    finally:
        await redis.aclose()
