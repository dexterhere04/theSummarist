FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Tesseract binary for OCR (pytesseract shells out to it).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies as a cached layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Application code + migrations.
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    STORAGE_LOCAL_DIR=/data/storage

EXPOSE 8000
