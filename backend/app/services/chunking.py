"""Section-aware chunking of extracted document text for map-reduce summarization.

Chunks are built at paragraph/bullet boundaries so no sentence is ever split,
and each chunk is prefixed with the section headings it covers so the map step
keeps structural context. Chunk size adapts upward when the document would
exceed the capped number of map calls.
"""
from __future__ import annotations


def flatten_body(body: list[dict] | None) -> list[tuple[str | None, str]]:
    """Flatten ExtractedText body into (heading, block) pairs.

    ``heading`` is the section heading the block belongs to (None if unknown).
    """
    blocks: list[tuple[str | None, str]] = []
    for section in body or []:
        heading = section.get("heading")
        heading = str(heading).strip() if heading else None
        for paragraph in section.get("paragraphs") or []:
            text = str(paragraph).strip()
            if text:
                blocks.append((heading, text))
        for bullet in section.get("bullets") or []:
            text = str(bullet).strip()
            if text:
                blocks.append((heading, f"- {text}"))
    return blocks


def chunk_blocks(
    blocks: list[tuple[str | None, str]],
    *,
    chunk_chars: int,
    max_chunks: int,
) -> list[str]:
    """Pack blocks into chunks of at most ``chunk_chars`` split on boundaries.

    If the document would produce more than ``max_chunks`` chunks, the size
    budget is scaled up so the whole document always fits within the cap.
    """
    if not blocks:
        return []

    total_chars = sum(len(text) for _, text in blocks)
    budget = max(chunk_chars, -(-total_chars // max_chunks))

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    current_heading: str | None = None

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append("\n\n".join(current))
        current = []
        current_len = 0

    for heading, text in blocks:
        # A single oversized block is hard-split on its character budget as a
        # last resort (no paragraph boundary available inside it).
        if len(text) > budget:
            flush()
            current_heading = None
            prefix = f"[{heading}]\n" if heading else ""
            for i in range(0, len(text), budget):
                chunks.append(prefix + text[i : i + budget])
            continue

        header_len = (
            len(f"[{heading}]\n") if heading and heading != current_heading else 0
        )
        if current and current_len + header_len + len(text) > budget:
            flush()
            current_heading = None

        if heading and heading != current_heading:
            header = f"[{heading}]\n"
            current.append(header + text)
            current_len += len(header) + len(text)
        else:
            current.append(text)
            current_len += len(text)
        current_heading = heading

    flush()
    return chunks


def prefix_for(heading: str | None, current_heading: str | None) -> str:
    if heading and heading != current_heading:
        return f"[{heading}]\n"
    return ""
