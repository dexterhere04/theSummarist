"""Deterministic stub text-to-speech service."""
from __future__ import annotations

import uuid

from app.config import settings


async def generate_audio(text: str, voice: str = "default") -> dict:
    words = len(text.split())
    duration_seconds = max(10, round(words / 150 * 60))
    audio_url = f"{settings.public_base_url}/audio/{uuid.uuid4().hex}.mp3"
    return {
        "audio_url": audio_url,
        "duration_seconds": duration_seconds,
        "voice": voice,
    }
