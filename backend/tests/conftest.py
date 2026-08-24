"""Test bootstrap: configure env BEFORE any app import."""
from __future__ import annotations

import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["STORAGE_LOCAL_DIR"] = tempfile.mkdtemp(prefix="summarist-storage-")
os.environ["LLM_API_KEY"] = ""  # force deterministic mock summarizer

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base, engine
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def _create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_headers(client):
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@summarist.ai", "password": "supersecret1", "name": "Test"},
    )
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


SAMPLE_TXT = (
    "Quarterly Business Review\n"
    "\n"
    "Revenue grew strongly this quarter driven by enterprise demand.\n"
    "Gross margin improved to 72 percent.\n"
    "\n"
    "- Enterprise revenue: 24 percent growth\n"
    "- Churn fell to 1.2 percent\n"
)


@pytest_asyncio.fixture
async def ready_document(client, auth_headers):
    res = await client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("qbr.txt", SAMPLE_TXT.encode(), "text/plain")},
        data={"run_summary": "false"},
    )
    assert res.status_code == 202, res.text
    doc = res.json()["document"]

    from app.services.pipeline import run_job

    job = res.json()["job"]
    await run_job(job["id"])
    return doc["id"]
