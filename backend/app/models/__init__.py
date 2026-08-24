"""Model registry — importing this registers all tables on Base.metadata."""
from app.models.document import Document, ExtractedText
from app.models.job import Job
from app.models.summary import ShareToken, Summary
from app.models.user import User, UserSettings

__all__ = [
    "Document",
    "ExtractedText",
    "Job",
    "ShareToken",
    "Summary",
    "User",
    "UserSettings",
]
