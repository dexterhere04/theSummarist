"""Unit tests for section-aware chunking."""
from __future__ import annotations

from app.services.chunking import chunk_blocks, flatten_body


def _blocks(*paragraphs: str) -> list[tuple[str | None, str]]:
    return [(None, p) for p in paragraphs]


def test_flatten_body_pairs_headings():
    body = [
        {
            "heading": "Intro",
            "paragraphs": ["First paragraph.", "Second paragraph."],
            "bullets": ["Point one"],
        }
    ]
    blocks = flatten_body(body)
    assert blocks == [
        ("Intro", "First paragraph."),
        ("Intro", "Second paragraph."),
        ("Intro", "- Point one"),
    ]


def test_flatten_body_empty():
    assert flatten_body([]) == []
    assert flatten_body(None) == []


def test_chunks_respect_budget():
    blocks = _blocks(*[f"Paragraph {i} " + "x" * 100 for i in range(20)])
    chunks = chunk_blocks(blocks, chunk_chars=400, max_chunks=48)
    assert len(chunks) > 1
    for c in chunks[:-1]:
        assert len(c) <= 400 + 200  # budget plus one block overshoot allowance


def test_no_block_split_when_fits():
    blocks = _blocks("Short one.", "Short two.", "Short three.")
    chunks = chunk_blocks(blocks, chunk_chars=10_000, max_chunks=48)
    assert chunks == ["Short one.\n\nShort two.\n\nShort three."]


def test_oversized_single_block_hard_split():
    big = "y" * 5_000
    blocks = _blocks(big)
    chunks = chunk_blocks(blocks, chunk_chars=1_000, max_chunks=48)
    assert len(chunks) == 5
    assert "".join(c for c in chunks) == big


def test_budget_scales_to_cap_max_map_calls():
    # 120 blocks x 5000 chars = 600k chars; with chunk_chars=12k that would be
    # 50 chunks, above the cap of 40 — budget must scale up so all content fits.
    blocks = _blocks(*["z" * 5_000 for _ in range(120)])
    chunks = chunk_blocks(blocks, chunk_chars=12_000, max_chunks=40)
    assert len(chunks) <= 40
    assert sum(len(c) for c in chunks) >= 600_000


def test_section_heading_prefix_included():
    body = [
        {"heading": "Finance", "paragraphs": ["Revenue rose."]},
        {"heading": "Tech", "paragraphs": ["Ship faster."]},
    ]
    blocks = flatten_body(body)
    chunks = chunk_blocks(blocks, chunk_chars=10_000, max_chunks=48)
    joined = "\n".join(chunks)
    assert "[Finance]" in joined and "[Tech]" in joined
