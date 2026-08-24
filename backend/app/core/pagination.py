"""Pagination helpers (backend.md §1.2)."""
from __future__ import annotations

from typing import Any


def clamp_page(page: int) -> int:
    return max(page, 1)


def clamp_per_page(per_page: int, default: int = 20, maximum: int = 100) -> int:
    if per_page < 1:
        return default
    return min(per_page, maximum)


def offset(page: int, per_page: int) -> int:
    return (page - 1) * per_page


def build_page(items: list[Any], page: int, per_page: int, total: int) -> dict[str, Any]:
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_more": page * per_page < total,
    }
