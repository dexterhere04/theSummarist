"""Summarization contract that turns extracted text into a structured summary.

Adaptive by length:

- Short documents (fits ``llm_max_input_chars``): single LLM call.
- Longer documents: section-aware chunking + parallel map calls producing
  intermediate notes, then a reduce call (hierarchical when notes themselves
  exceed the context budget) producing the §2.4 contract.

Total map calls are capped (``llm_max_map_calls``) so cost is bounded no
matter how long the input is — chunk size scales up instead of dropping
content.
"""
from __future__ import annotations

import asyncio
import re

from app.config import settings
from app.core.errors import UpstreamError
from app.services.chunking import chunk_blocks
from app.services.llm import llm_client

ALLOWED_CATEGORIES = {"Research", "Finance", "Tech", "Internal"}
REQUIRED_KEYS = ("tldr", "excerpt", "takeaways", "sections", "highlight", "category")
# Intermediate map/condense calls produce short notes — a tight token cap keeps
# latency low; only the final reduce gets the full output budget.
_MAP_MAX_TOKENS = 1_200


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _first_sentences(text: str, n: int = 2) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return ""
    return " ".join(sentences[:n])


def _longest_sentence(text: str) -> str | None:
    sentences = _split_sentences(text)
    if not sentences:
        return None
    return max(sentences, key=len)


def _mock_takeaways(text: str) -> list[dict]:
    words = text.split()
    if not words:
        return [
            {"title": f"Key Point {i + 1}", "body": "No content available."}
            for i in range(3)
        ]
    result = []
    for i in range(3):
        chunk = " ".join(words[i * 5 : i * 5 + 5])
        result.append({"title": f"Key Point {i + 1}", "body": chunk})
    return result


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------


def _build_prompts(
    truncated: str,
    length: str,
    style: str,
    fmt: str,
    detail_level: str,
    include_key_points: bool,
    include_quotes: bool,
) -> tuple[str, str]:
    system = (
        "You are a document summarizer. Return only a single JSON object with exactly these keys: "
        '"tldr" (string, a 2-4 sentence quick summary), '
        '"excerpt" (string, a 1-2 sentence subtitle), '
        '"takeaways" (a list of objects, each with a "title" string and a "body" string), '
        '"sections" (a list of objects, each with a "heading" string and a "body" string), '
        '"highlight" (a short notable quote string, or null), '
        '"category" (a string). '
        f'Because include_key_points is {include_key_points}, "takeaways" must be '
        f'{"a list of objects" if include_key_points else "an empty list []"}. '
        f'Because include_quotes is {include_quotes}, "highlight" must be '
        f'{"a short quote string" if include_quotes else "null"}. '
        '"category" must be exactly one of: "Research", "Finance", "Tech", "Internal". '
        "Return valid JSON only, with no extra text."
    )
    user = (
        f"Length: {length}\n"
        f"Style: {style}\n"
        f"Format: {fmt}\n"
        f"Detail level: {detail_level}\n"
        f"Include key points: {include_key_points}\n"
        f"Include quotes: {include_quotes}\n\n"
        f"Text:\n{truncated}"
    )
    return system, user


_MAP_SYSTEM = (
    "You are a document analysis assistant. You will be given one part of a "
    "longer document. Extract its essential content as intermediate notes for a "
    "later summarization step. Return only a single JSON object with keys: "
    '"summary" (string, a dense paragraph capturing every important point in '
    "this part, preserving concrete numbers, names, dates and conclusions), "
    '"key_facts" (list of strings, the most important individual facts or '
    "arguments, verbatim where possible). "
    "Do not comment on the part being an excerpt. Return valid JSON only."
)


def _map_user(chunk: str) -> str:
    return f"Document part:\n{chunk}"


_REDUCE_SYSTEM_TMPL = (
    "You are a document summarizer. You will be given structured notes extracted "
    "from every part of one long document. Synthesize them into a final summary. "
    "Return only a single JSON object with exactly these keys: "
    '"tldr" (string, a 2-4 sentence quick summary), '
    '"excerpt" (string, a 1-2 sentence subtitle), '
    '"takeaways" (a list of objects, each with a "title" string and a "body" string), '
    '"sections" (a list of objects, each with a "heading" string and a "body" string '
    "covering the document's major themes in order), "
    '"highlight" (a short notable quote string taken from the notes, or null), '
    '"category" (a string). '
    'Because include_key_points is {include_key_points}, "takeaways" must be '
    '{takeaways_clause}. '
    'Because include_quotes is {include_quotes}, "highlight" must be '
    '{quotes_clause}. '
    '"category" must be exactly one of: "Research", "Finance", "Tech", "Internal". '
    "Never invent content absent from the notes. Return valid JSON only."
)

_CONDENSE_SYSTEM = (
    "You are a document analysis assistant. You will be given notes extracted "
    "from parts of one long document. Merge them into a shorter set of notes "
    "that preserves all distinct important facts, numbers, names and "
    "conclusions. Return only a single JSON object with keys: "
    '"summary" (string, dense synthesis paragraph) and '
    '"key_facts" (list of strings). Return valid JSON only.'
)


# --------------------------------------------------------------------------
# Validation / normalization (shared by single-pass and reduce outputs)
# --------------------------------------------------------------------------


def _is_valid(result: object) -> bool:
    if not isinstance(result, dict):
        return False
    if any(key not in result for key in REQUIRED_KEYS):
        return False
    if not isinstance(result["tldr"], str) or not result["tldr"].strip():
        return False
    if not isinstance(result["excerpt"], str) or not result["excerpt"].strip():
        return False
    if not isinstance(result["takeaways"], list):
        return False
    if not isinstance(result["sections"], list):
        return False
    if not isinstance(result["highlight"], (str, type(None))):
        return False
    return isinstance(result["category"], str)


def _normalize_items(items: object, key_a: str, key_b: str) -> list[dict]:
    if not isinstance(items, list):
        return []
    result: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        a = item.get(key_a)
        b = item.get(key_b)
        if isinstance(a, str) and isinstance(b, str) and a.strip() and b.strip():
            result.append({key_a: a.strip(), key_b: b.strip()})
    return result


def _normalize_notes(candidate: object, chunk: str) -> dict:
    """Normalize a map/condense response into {"summary", "key_facts"}."""
    summary = ""
    key_facts: list[str] = []
    if isinstance(candidate, dict):
        s = candidate.get("summary")
        if isinstance(s, str):
            summary = s.strip()
        facts = candidate.get("key_facts")
        if isinstance(facts, list):
            key_facts = [str(f).strip() for f in facts if str(f).strip()]
    if not summary:
        summary = _first_sentences(chunk, n=6) or chunk[:600]
    if not key_facts:
        key_facts = [s for s in _split_sentences(chunk)[:5]]
    return {"summary": summary, "key_facts": key_facts}


def _normalize(
    result: dict,
    truncated: str,
    *,
    include_key_points: bool | None = None,
    include_quotes: bool | None = None,
) -> dict:
    tldr = result.get("tldr")
    if not isinstance(tldr, str) or not tldr.strip():
        tldr = _first_sentences(truncated) or "The document has been summarized."

    excerpt = result.get("excerpt")
    if not isinstance(excerpt, str) or not excerpt.strip():
        excerpt = truncated[:180]
        if len(truncated) > 180:
            excerpt += "..."

    takeaways = _normalize_items(result.get("takeaways"), "title", "body")
    sections = _normalize_items(result.get("sections"), "heading", "body")
    if include_key_points is False:
        takeaways = []

    highlight = result.get("highlight")
    if not isinstance(highlight, str) or not highlight.strip():
        highlight = None
    if include_quotes is False:
        highlight = None

    category = result.get("category")
    if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
        category = "Research"

    return {
        "tldr": tldr,
        "excerpt": excerpt,
        "takeaways": takeaways,
        "sections": sections,
        "highlight": highlight,
        "category": category,
    }


def _notes_to_text(notes: list[dict]) -> str:
    parts: list[str] = []
    for i, note in enumerate(notes, start=1):
        facts = "\n".join(f"- {f}" for f in note["key_facts"])
        parts.append(f"[Part {i}]\n{note['summary']}\n{facts}".strip())
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# LLM steps with retries
# --------------------------------------------------------------------------


async def _chat_json_with_retry(
    system: str, user: str, attempts: int = 3, *, max_tokens: int | None = None
) -> dict | None:
    for _ in range(attempts):
        try:
            candidate = await llm_client.chat_json(system, user, max_tokens=max_tokens)
        except UpstreamError:
            continue
        if candidate is not None:
            return candidate
    return None


async def _map_chunk(chunk: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        candidate = await _chat_json_with_retry(
            _MAP_SYSTEM, _map_user(chunk), max_tokens=_MAP_MAX_TOKENS
        )
    return _normalize_notes(candidate, chunk)


async def _map_chunks(chunks: list[str]) -> list[dict]:
    semaphore = asyncio.Semaphore(settings.llm_map_concurrency)
    results = await asyncio.gather(*(_map_chunk(c, semaphore) for c in chunks))
    return list(results)


async def _condense_notes(notes_text: str) -> dict:
    candidate = await _chat_json_with_retry(
        _CONDENSE_SYSTEM,
        f"Notes:\n{notes_text}",
        max_tokens=_MAP_MAX_TOKENS,
    )
    return _normalize_notes(candidate, notes_text)


async def _final_reduce(
    notes: list[dict],
    *,
    length: str,
    style: str,
    fmt: str,
    detail_level: str,
    include_key_points: bool,
    include_quotes: bool,
) -> dict:
    system = _REDUCE_SYSTEM_TMPL.format(
        include_key_points=include_key_points,
        takeaways_clause=(
            "a list of objects" if include_key_points else "an empty list []"
        ),
        include_quotes=include_quotes,
        quotes_clause=(
            "a short quote string" if include_quotes else "null"
        ),
    )
    user = (
        f"Length: {length}\n"
        f"Style: {style}\n"
        f"Format: {fmt}\n"
        f"Detail level: {detail_level}\n\n"
        f"Notes from all document parts:\n{_notes_to_text(notes)}"
    )
    for _ in range(3):
        candidate = await _chat_json_with_retry(system, user, attempts=1)
        if candidate is not None and _is_valid(candidate):
            return candidate
    raise UpstreamError("Summarization failed")


# --------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------


async def summarize_text(
    text: str,
    *,
    length: str,
    style: str,
    fmt: str,
    detail_level: str,
    include_key_points: bool,
    include_quotes: bool,
    blocks: list[tuple[str | None, str]] | None = None,
) -> dict:
    """Summarize arbitrary text adaptively by length.

    ``blocks`` optionally supplies (heading, block) pairs used for
    structure-preserving chunking on the map-reduce path.
    """
    if not settings.llm_api_key:
        # No provider configured: deterministic extractive mock over full text.
        truncated = text[: settings.llm_max_input_chars]
        excerpt = truncated[:180]
        if len(truncated) > 180:
            excerpt += "..."
        return {
            "tldr": _first_sentences(truncated) or "The document has been summarized.",
            "excerpt": excerpt,
            "takeaways": _mock_takeaways(truncated) if include_key_points else [],
            "sections": [
                {"heading": "Overview", "body": truncated[: len(truncated) // 2]},
                {"heading": "Details", "body": truncated[len(truncated) // 2 :]},
            ],
            "highlight": _longest_sentence(truncated) if include_quotes else None,
            "category": "Research",
        }

    if len(text) <= settings.llm_max_input_chars:
        system, user = _build_prompts(
            text, length, style, fmt, detail_level,
            include_key_points, include_quotes,
        )
        result: dict | None = None
        for _ in range(3):
            candidate = await llm_client.chat_json(system, user)
            if _is_valid(candidate):
                result = candidate
                break
        if result is None:
            raise UpstreamError("Summarization failed")
        return _normalize(
            result,
            text[:4000],
            include_key_points=include_key_points,
            include_quotes=include_quotes,
        )

    return await _summarize_map_reduce(
        text,
        blocks=blocks,
        length=length,
        style=style,
        fmt=fmt,
        detail_level=detail_level,
        include_key_points=include_key_points,
        include_quotes=include_quotes,
    )


async def _summarize_map_reduce(
    text: str,
    *,
    blocks: list[tuple[str | None, str]] | None,
    length: str,
    style: str,
    fmt: str,
    detail_level: str,
    include_key_points: bool,
    include_quotes: bool,
) -> dict:
    if blocks:
        chunks = chunk_blocks(
            blocks,
            chunk_chars=settings.llm_chunk_chars,
            max_chunks=settings.llm_max_map_calls,
        )
    else:
        total = len(text)
        budget = max(
            settings.llm_chunk_chars,
            -(-total // settings.llm_max_map_calls),
        )
        chunks = [text[i : i + budget] for i in range(0, total, budget)]

    notes = await _map_chunks(chunks)

    # Hierarchical condensation while notes exceed the context budget.
    max_notes_chars = settings.llm_max_input_chars - 2000
    while len(_notes_to_text(notes)) > max_notes_chars:
        group_size = max(2, len(notes) // 8)
        semaphore = asyncio.Semaphore(settings.llm_map_concurrency)

        async def condense_group(
            group: list[dict], semaphore: asyncio.Semaphore = semaphore
        ) -> dict:
            async with semaphore:
                return await _condense_notes(_notes_to_text(group))

        grouped = [
            notes[i : i + group_size] for i in range(0, len(notes), group_size)
        ]
        notes = list(await asyncio.gather(*(condense_group(g) for g in grouped)))
        if len(notes) <= 2:
            break

    result = await _final_reduce(
        notes,
        length=length,
        style=style,
        fmt=fmt,
        detail_level=detail_level,
        include_key_points=include_key_points,
        include_quotes=include_quotes,
    )
    return _normalize(
        result,
        text[:4000],
        include_key_points=include_key_points,
        include_quotes=include_quotes,
    )
