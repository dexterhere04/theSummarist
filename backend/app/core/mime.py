"""MIME type → DocFormat mapping and upload validation (backend.md §3.3)."""
from __future__ import annotations

from app.models.enums import DocFormat

# Images are accepted per §3.3 but DocFormat has no image member; scanned images
# are OCR'd and treated as single-page PDF documents for the rest of the pipeline.
MIME_TO_FORMAT: dict[str, DocFormat] = {
    "application/pdf": DocFormat.PDF,
    "text/plain": DocFormat.TXT,
    "application/msword": DocFormat.DOC,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocFormat.DOCX,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": DocFormat.PPTX,
    "image/png": DocFormat.PDF,
    "image/jpeg": DocFormat.PDF,
    "image/jpg": DocFormat.PDF,
}

ALLOWED_MIMES = frozenset(MIME_TO_FORMAT.keys())


def format_for_mime(mime_type: str) -> DocFormat | None:
    return MIME_TO_FORMAT.get(mime_type.lower())


def is_allowed_mime(mime_type: str) -> bool:
    return mime_type.lower() in ALLOWED_MIMES
