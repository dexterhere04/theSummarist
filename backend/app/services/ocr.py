"""OCR extraction via pytesseract."""
from __future__ import annotations

import io

import pytesseract
from PIL import Image

from app.config import settings
from app.core.errors import ExtractionFailedError

pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def ocr_image(data: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(image)
    except Exception as e:
        raise ExtractionFailedError(f"OCR failed: {e}") from e
