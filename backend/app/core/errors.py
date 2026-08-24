"""Centralized error envelope and HTTP exception handling.

Error shape (backend.md §1.2):
    { "error": { "code", "message", "details?" } }
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class APIError(Exception):
    """Base class for domain errors that map to a stable error envelope."""

    status_code = 500
    code = "INTERNAL"
    message = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: Any = None,
    ) -> None:
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = details
        super().__init__(self.message)

    def envelope(self) -> dict[str, Any]:
        body: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            body["details"] = self.details
        return {"error": body}


class UnauthenticatedError(APIError):
    status_code = 401
    code = "UNAUTHENTICATED"
    message = "Authentication required."


class ForbiddenError(APIError):
    status_code = 403
    code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class NotFoundError(APIError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found."


class ConflictError(APIError):
    status_code = 409
    code = "CONFLICT"
    message = "Resource is in an invalid state."


class JobAlreadyRunningError(APIError):
    status_code = 409
    code = "JOB_ALREADY_RUNNING"
    message = "A job is already running for this resource."


class FileTooLargeError(APIError):
    status_code = 413
    code = "FILE_TOO_LARGE"
    message = "File exceeds the maximum allowed size."


class UnsupportedTypeError(APIError):
    status_code = 415
    code = "UNSUPPORTED_TYPE"
    message = "Unsupported file type."


class InvalidURLError(APIError):
    status_code = 422
    code = "INVALID_URL"
    message = "The provided URL is invalid or unreachable."


class ExtractionFailedError(APIError):
    status_code = 422
    code = "EXTRACTION_FAILED"
    message = "Failed to extract text from the document."


class RateLimitedError(APIError):
    status_code = 429
    code = "RATE_LIMITED"
    message = "Rate limit exceeded."


class UpstreamError(APIError):
    status_code = 502
    code = "UPSTREAM_ERROR"
    message = "An upstream provider failed."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def _api_error_handler(_: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.envelope())

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Malformed request.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "NOT_FOUND" if exc.status_code == 404 else "INTERNAL"
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": code, "message": str(exc.detail)}},
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL", "message": "Internal server error."}},
        )
