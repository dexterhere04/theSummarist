"""Domain enumerations. Values must match backend.md §1.3 exactly."""
from __future__ import annotations

import enum


class DocFormat(str, enum.Enum):
    PDF = "PDF"
    DOC = "DOC"
    DOCX = "DOCX"
    PPTX = "PPTX"
    TXT = "TXT"
    WEB = "WEB"


class DocStatus(str, enum.Enum):
    uploaded = "uploaded"
    extracting = "extracting"
    understanding = "understanding"
    preparing = "preparing"
    ready = "ready"
    failed = "failed"


class DocSource(str, enum.Enum):
    upload = "upload"
    url = "url"


class SummaryLength(str, enum.Enum):
    Short = "Short"
    Medium = "Medium"
    Long = "Long"


class SummaryStyle(str, enum.Enum):
    executive = "executive"
    key_points = "key_points"
    detailed = "detailed"
    study_notes = "study_notes"
    action_items = "action_items"


class SummaryFormat(str, enum.Enum):
    bullets = "bullets"
    paragraph = "paragraph"


class DetailLevel(str, enum.Enum):
    concise = "concise"
    medium = "medium"
    detailed = "detailed"


class Category(str, enum.Enum):
    Research = "Research"
    Finance = "Finance"
    Tech = "Tech"
    Internal = "Internal"


class SummaryStatus(str, enum.Enum):
    ready = "ready"
    generating = "generating"
    failed = "failed"


class JobType(str, enum.Enum):
    extract = "extract"
    summarize = "summarize"


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class JobStage(str, enum.Enum):
    uploaded = "uploaded"
    extracting = "extracting"
    understanding = "understanding"
    preparing = "preparing"


STYLE_KIND_MAP: dict[str, str] = {
    "executive": "Executive Summary",
    "key_points": "Key Points",
    "detailed": "Detailed Summary",
    "study_notes": "Study Notes",
    "action_items": "Action Items",
}

# Ordered pipeline stages and their client-facing step index (backend.md §2.5).
PIPELINE_STAGES: list[JobStage] = [
    JobStage.uploaded,
    JobStage.extracting,
    JobStage.understanding,
    JobStage.preparing,
]
TOTAL_STAGES = len(PIPELINE_STAGES)
