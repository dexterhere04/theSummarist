"""Tests for the adaptive summarizer (single-pass vs map-reduce)."""
from __future__ import annotations

import json

import pytest

from app.config import settings
from app.core.errors import UpstreamError
from app.services import summarizer
from app.services.llm import llm_client

FINAL_VALID = {
    "tldr": "The doc says things.",
    "excerpt": "A subtitle.",
    "takeaways": [{"title": "T", "body": "B"}],
    "sections": [{"heading": "H", "body": "Body text."}],
    "highlight": "quote",
    "category": "Tech",
}


class FakeLLM:
    """Records calls and returns scripted responses."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []
        self.script: list[object] = []

    def queue(self, *responses: object) -> None:
        self.script.extend(responses)

    async def chat_json(self, system: str, user: str, **_: object) -> dict:
        self.calls.append((system, user))
        if not self.script:
            raise UpstreamError("script exhausted")
        resp = self.script.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(summarizer, "llm_client", fake)
    return fake


@pytest.fixture(autouse=True)
def enable_key(monkeypatch):
    monkeypatch.setattr(settings, "llm_api_key", "test-key")


def _long_text(n_chars: int = 130_000) -> str:
    sentence = "The committee reviewed quarterly performance metrics carefully. "
    return (sentence * (n_chars // len(sentence) + 1))[:n_chars]


async def test_short_doc_single_call(fake_llm):
    fake_llm.queue(FINAL_VALID)
    result = await summarizer.summarize_text(
        "Short document text.",
        length="Medium",
        style="executive",
        fmt="bullets",
        detail_level="concise",
        include_key_points=True,
        include_quotes=True,
    )
    assert len(fake_llm.calls) == 1
    assert result["tldr"] == "The doc says things."
    assert result["category"] == "Tech"


async def test_long_doc_uses_map_reduce(fake_llm, monkeypatch):
    monkeypatch.setattr(settings, "llm_max_input_chars", 60_000)
    monkeypatch.setattr(settings, "llm_chunk_chars", 12_000)
    text = _long_text(130_000)

    # One map response per chunk (11 chunks), then the reduce call.
    n_chunks = -(-len(text) // 12_000)
    fake_llm.queue(*[{"summary": f"part {i}", "key_facts": [f"fact {i}"]}
                     for i in range(n_chunks)])
    fake_llm.queue(FINAL_VALID)

    result = await summarizer.summarize_text(
        text,
        length="Long",
        style="detailed",
        fmt="paragraph",
        detail_level="detailed",
        include_key_points=False,
        include_quotes=False,
    )

    assert len(result["takeaways"]) == 0
    assert result["highlight"] is None
    map_calls = fake_llm.calls[:-1]
    assert len(map_calls) == n_chunks
    # Reduce prompt must contain every part's notes.
    _, reduce_user = fake_llm.calls[-1]
    for i in range(n_chunks):
        assert f"part {i}" in reduce_user


async def test_map_reduce_caps_total_calls(fake_llm, monkeypatch):
    monkeypatch.setattr(settings, "llm_max_input_chars", 10_000)
    monkeypatch.setattr(settings, "llm_chunk_chars", 5_000)
    monkeypatch.setattr(settings, "llm_max_map_calls", 8)
    text = _long_text(200_000)  # would be 40 chunks at 5k — capped to 8

    fake_llm.queue(*[{"summary": "s", "key_facts": []} for _ in range(8)])
    fake_llm.queue(FINAL_VALID)

    await summarizer.summarize_text(
        text,
        length="Medium",
        style="executive",
        fmt="bullets",
        detail_level="medium",
        include_key_points=True,
        include_quotes=True,
    )
    assert len(fake_llm.calls) <= 9  # 8 maps + 1 reduce


async def test_map_failures_fall_back_extractive(fake_llm, monkeypatch):
    monkeypatch.setattr(settings, "llm_max_input_chars", 10_000)
    monkeypatch.setattr(settings, "llm_chunk_chars", 12_000)
    text = _long_text(30_000)
    n_chunks = -(-len(text) // 12_000)

    fake_llm.queue(*[UpstreamError("boom")] * (n_chunks * 3))
    fake_llm.queue(FINAL_VALID)

    result = await summarizer.summarize_text(
        text,
        length="Short",
        style="key_points",
        fmt="bullets",
        detail_level="concise",
        include_key_points=True,
        include_quotes=False,
    )
    # Fallback notes are extractive first sentences of each chunk.
    _, reduce_user = fake_llm.calls[-1]
    assert "[Part 1]" in reduce_user
    assert result["tldr"] == "The doc says things."


async def test_reduce_invalid_output_raises(fake_llm, monkeypatch):
    monkeypatch.setattr(settings, "llm_max_input_chars", 10_000)
    text = _long_text(25_000)
    fake_llm.queue(*[{"summary": "s", "key_facts": []}] * 3)  # 3 chunks mapped
    fake_llm.queue({"tldr": ""})  # invalid reduce outputs x3 attempts
    fake_llm.queue({"tldr": ""})
    fake_llm.queue({"tldr": ""})

    with pytest.raises(UpstreamError):
        await summarizer.summarize_text(
            text,
            length="Short",
            style="executive",
            fmt="bullets",
            detail_level="concise",
            include_key_points=True,
            include_quotes=False,
        )


async def test_no_api_key_mock_covers_full_short_text(monkeypatch):
    monkeypatch.setattr(settings, "llm_api_key", "")
    result = await summarizer.summarize_text(
        "One two three four five six seven eight nine ten.",
        length="Short",
        style="executive",
        fmt="bullets",
        detail_level="concise",
        include_key_points=True,
        include_quotes=True,
    )
    assert result["highlight"]
    assert len(result["takeaways"]) == 3


def test_normalize_clamps_bad_category():
    raw = {
        **FINAL_VALID,
        "category": "Sports",
        "takeaways": [{"title": "", "body": "dropped"}],
    }
    normalized = summarizer._normalize(raw, "some source text")
    assert normalized["category"] == "Research"
    assert normalized["takeaways"] == []


def test_chat_json_extracts_embedded_json(monkeypatch):
    content = f"Here you go:\n```json\n{json.dumps(FINAL_VALID)}\n```"
    sse_lines = [
        f'data: {json.dumps({"choices": [{"delta": {"content": chunk}}]})}'
        for chunk in [content[:40], content[40:80], content[80:]]
    ] + ["data: [DONE]"]

    class Resp:
        status_code = 200

        async def aread(self):
            return b""

        async def aiter_lines(self):
            for line in sse_lines:
                yield line

    class StreamCtx:
        async def __aenter__(self):
            return Resp()

        async def __aexit__(self, *exc):
            return False

    class FakeAsyncClient:
        def stream(self, method, url, headers=None, json=None):
            return StreamCtx()

    import httpx as _httpx

    monkeypatch.setattr(_httpx, "AsyncClient", lambda timeout: FakeAsyncClient())
    result = __import__("asyncio").get_event_loop().run_until_complete(
        llm_client.chat_json("sys", "usr")
    )
    assert result == FINAL_VALID
