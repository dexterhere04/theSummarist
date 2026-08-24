"""Storage abstraction for object persistence (local filesystem / S3)."""
from __future__ import annotations

from pathlib import Path

from app.config import settings


class Storage:
    async def put(self, key: str, data: bytes, content_type: str = "") -> None:
        raise NotImplementedError

    async def get(self, key: str) -> bytes:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError


class LocalStorage(Storage):
    def __init__(self, root: Path) -> None:
        self.root = root

    async def put(self, key: str, data: bytes, content_type: str = "") -> None:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    async def get(self, key: str) -> bytes:
        path = self.root / key
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self.root / key
        try:
            path.unlink()
        except FileNotFoundError:
            pass


class _NotImplementedStorage(Storage):
    async def put(self, key: str, data: bytes, content_type: str = "") -> None:
        raise NotImplementedError("S3 storage not configured")

    async def get(self, key: str) -> bytes:
        raise NotImplementedError("S3 storage not configured")

    async def delete(self, key: str) -> None:
        raise NotImplementedError("S3 storage not configured")


def get_storage() -> Storage:
    if settings.storage_backend == "local":
        return LocalStorage(settings.storage_local_dir)
    return _NotImplementedStorage()


storage = get_storage()
