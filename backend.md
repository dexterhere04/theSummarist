# TheSummarist — Backend API Specification

> Generated from a full analysis of `frontend/`. This document is the authoritative contract the backend must implement to power the existing React frontend **without modifying the frontend**.

---

## 1. Overview

**TheSummarist** is a document summarization product. A user uploads a document (or a web URL), the backend extracts its text (OCR + layout parsing), the user configures how they want it summarized, and the backend generates an AI summary (TL;DR, key takeaways, detailed sections, and a notable quote).

### 1.1 The frontend's journey (end-to-end)

1. **Dashboard** (`/`) — upload a document (PDF/PNG/JPG/JPEG, ≤ 50 MB), or browse existing summaries.
2. **Processing** (`/processing`) — a 4-step pipeline: *Document uploaded → Extracting text → Understanding document → Preparing summary*.
3. **Extracted text** (`/document/:id`) — review extracted text, search within it, copy, download as TXT, pick summary format + detail level.
4. **Configure** (`/configure`) — pick summary **Length** (Short/Medium/Long), **Style** (5 options), and toggles for key points + quotes.
5. **Summary** (`/summary/:id`) — read the generated summary, regenerate, download, favorite, share, listen (TTS), view source.
6. **Library** (`/summaries`, `/recent`, `/favorites`) — browse, filter by tab, search.
7. **Account** (`/settings`, `/profile`).

### 1.2 Base conventions

| Convention | Value |
|---|---|
| Base URL | `/api/v1` |
| Content type | `application/json` (uploads use `multipart/form-data`) |
| Auth | Bearer token (JWT) in `Authorization: Bearer <token>` header |
| Date/time | ISO-8601 UTC (`2026-08-22T14:45:00Z`) |
| Pagination | `?page=1&per_page=20` returning `{ items, page, per_page, total, has_more }` |
| Error shape | `{ error: { code, message, details? } }` |
| Idempotency | `POST /summaries` and `POST /documents` accept `Idempotency-Key` header |

### 1.3 Enumerations (must match frontend exactly)

```ts
DocFormat     = 'PDF' | 'DOC' | 'DOCX' | 'PPTX' | 'TXT' | 'WEB'
SummaryLength = 'Short' | 'Medium' | 'Long'
SummaryStyle  = 'executive' | 'key_points' | 'detailed' | 'study_notes' | 'action_items'
SummaryFormat = 'bullets' | 'paragraph'
DetailLevel   = 'concise' | 'medium' | 'detailed'
Category      = 'Research' | 'Finance' | 'Tech' | 'Internal'   // auto-classified, overridable
```

`SummaryStyle → kind` label mapping (used by the frontend `Chip tone="accent"`):

| style value | `kind` label |
|---|---|
| `executive` | Executive Summary |
| `key_points` | Key Points |
| `detailed` | Detailed Summary |
| `study_notes` | Study Notes |
| `action_items` | Action Items |

---

## 2. Data models

### 2.1 User

```json
{
  "id": "usr_01J...",
  "email": "dexter@summarist.ai",
  "name": "Dexter",
  "avatar_initials": "D",
  "plan": "free",
  "created_at": "2026-08-01T09:00:00Z"
}
```

### 2.2 Document (source file)

```json
{
  "id": "doc_01J...",
  "user_id": "usr_01J...",
  "file_name": "Q4_Financial_Report_2023_Final_Draft.pdf",
  "format": "PDF",
  "mime_type": "application/pdf",
  "size_bytes": 4404019,
  "source": "upload",
  "source_url": null,
  "status": "ready",
  "pages": 12,
  "words": 4285,
  "language": "English (US)",
  "ocr_method": "Advanced Vision V4",
  "created_at": "2026-08-22T14:43:00Z",
  "updated_at": "2026-08-22T14:45:00Z"
}
```

- `status`: `uploaded | extracting | understanding | preparing | ready | failed`
- `source`: `upload | url`
- `ocr_method`: engine label shown in "Document Properties" (e.g. `Advanced Vision V4`, `Native Text Layer`, `None`).

### 2.3 ExtractedText

```json
{
  "document_id": "doc_01J...",
  "title": "Q3 2023 Financial Performance Overview",
  "file_name": "Q3_Financial_Report_2023.pdf",
  "format": "PDF",
  "pages": 12,
  "words": 4285,
  "language": "English (US)",
  "ocr_method": "Advanced Vision V4",
  "body": [
    {
      "heading": "Executive Summary",
      "paragraphs": ["...", "..."],
      "bullets": ["Enterprise Subscriptions: $28.5 million ..."]
    }
  ]
}
```

> `bullets` is optional per section. `paragraphs` and `bullets` may coexist in a section.

### 2.4 Summary

```json
{
  "id": "sum_01J...",
  "document_id": "doc_01J...",
  "user_id": "usr_01J...",
  "title": "Quantum Computing Overview",
  "source": "quantum_computing_whitepaper.pdf",
  "format": "PDF",
  "excerpt": "How quantum mechanics is reshaping computation...",
  "date": "Today, 2:45 PM",
  "length": "Medium",
  "style": "executive",
  "kind": "Executive Summary",
  "category": "Research",
  "pages": 18,
  "words": 6420,
  "tldr": "Quantum computing leverages...",
  "takeaways": [
    { "title": "Superposition & Entanglement", "body": "..." }
  ],
  "sections": [
    { "heading": "The Paradigm Shift", "body": "..." }
  ],
  "highlight": "The strategic pivot towards quantum-safe cryptography...",
  "favorite": false,
  "status": "ready",
  "params": {
    "format": "bullets",
    "detail_level": "concise",
    "include_key_points": true,
    "include_quotes": false
  },
  "created_at": "2026-08-22T14:45:00Z"
}
```

- `date`: **relative display string** ("Today, 2:45 PM", "Yesterday", "Oct 10, 2025"). Recommended: store `created_at` (timestamp) and have the backend emit a pre-formatted `date` for the client, OR return `created_at` and let the client format. The frontend currently reads `date` directly, so the API returns it pre-formatted to match the UI.
- `params`: the configuration used to generate this summary (used by "Regenerate").
- `favorite`: boolean; `status`: `ready | generating | failed`.

### 2.5 Processing Job

```json
{
  "id": "job_01J...",
  "document_id": "doc_01J...",
  "type": "extract | summarize",
  "status": "pending | running | succeeded | failed | cancelled",
  "stage": "uploaded | extracting | understanding | preparing",
  "progress": 0..100,
  "stage_index": 2,
  "total_stages": 4,
  "error": null,
  "created_at": "2026-08-22T14:43:00Z"
}
```

The frontend `Processing.tsx` renders **4 steps** with states `done | active | pending`. The backend must expose `stage` so the client can map:

| stage | step index | client state |
|---|---|---|
| `uploaded` | 0 (Document uploaded) | done |
| `extracting` | 1 (Extracting text) | done |
| `understanding` | 2 (Understanding document) | active |
| `preparing` | 3 (Preparing summary) | pending |

---

## 3. API endpoints

### 3.1 Authentication

#### `POST /api/v1/auth/register`
Create an account.
- Body: `{ "email": string, "password": string, "name": string }`
- 201: `{ "user": User, "access_token": string, "refresh_token": string }`
- 409: email already registered.

#### `POST /api/v1/auth/login`
- Body: `{ "email": string, "password": string }`
- 200: `{ "user": User, "access_token": string, "refresh_token": string }`
- 401: invalid credentials.

#### `POST /api/v1/auth/refresh`
- Body: `{ "refresh_token": string }`
- 200: `{ "access_token": string, "refresh_token": string }`

#### `POST /api/v1/auth/logout`
- Body: `{ "refresh_token": string }` — revokes the token.
- 204.

---

### 3.2 User & account

#### `GET /api/v1/me`
Returns the authenticated user (feeds the sidebar footer: `Dexter` / `dexter@summarist.ai`).
- 200: `User`

#### `PATCH /api/v1/me`
Update name/email.
- Body: `{ "name"?: string, "email"?: string }`
- 200: `User`

#### `GET /api/v1/me/settings`
User preferences (default length/style, language, TTS voice, theme).
- 200: `{ "default_length": "Medium", "default_style": "executive", "language": "en-US", "tts_voice": "default", "theme": "light" }`

#### `PATCH /api/v1/me/settings`
- Body: partial settings object.
- 200: updated settings.

---

### 3.3 Documents (upload, extraction, processing)

#### `POST /api/v1/documents` — upload a document
`multipart/form-data`:
| field | type | notes |
|---|---|---|
| `file` | file (required) | PDF, PNG, JPG, JPEG, DOC, DOCX, PPTX, TXT |
| `title`? | string | optional title override |
| `run_summary`? | bool | default `true`; if false only extract |

Validation:
- Max size **50 MB** (frontend copy says "up to 50 MB").
- Allowed mime types → map to `DocFormat`.
- Reject with `413` (too large) / `415` (unsupported type).

Response:
- 202 Accepted: `{ "document": Document, "job": ProcessingJob }`

Behavior: store the file, create a `Document` (status `uploaded`), enqueue an **extract** job. The job drives the `/processing` pipeline. On success the document is reachable at `/document/:id`.

#### `POST /api/v1/documents/from-url` — summarize a web page (WEB format)
- Body: `{ "url": string }`
- 202: `{ "document": Document, "job": ProcessingJob }`
- 422: invalid/unreachable URL.
- Fetches page, extracts main content, treats as `format: "WEB"`.

#### `GET /api/v1/documents` — recent documents
- Query: `?page&per_page&q` (search by file name).
- 200: paginated `{ "items": Document[], ... }` sorted by `created_at desc`.
- Powers `/recent`.

#### `GET /api/v1/documents/:id`
- 200: `Document`
- 404.

#### `DELETE /api/v1/documents/:id`
Soft-delete the document and its summaries.
- 204.

#### `GET /api/v1/documents/:id/status` — processing status
- 200: `ProcessingJob` (current stage/progress).
- Used to poll while on `/processing`. (See 3.6 for streaming.)

#### `GET /api/v1/documents/:id/extracted-text` — extracted text (ExtractedText page)
- 200: `ExtractedText`
- 409: still processing (extraction not complete).

#### `GET /api/v1/documents/:id/download` — original file
- 200: binary (`Content-Disposition: attachment`).

#### `GET /api/v1/documents/:id/export.txt` — "Download TXT"
- 200: `text/plain` (the extracted body flattened to text).

#### `GET /api/v1/documents/:id/search?q=...` — search within text
- 200: `{ "matches": [ { "section_heading": string, "paragraph_index": number, "snippet": string, "start": number, "end": number } ], "total": number }`
- Powers the "Search text…" input on the ExtractedText page.

---

### 3.4 Summaries

#### `POST /api/v1/summaries` — generate a summary
Creates the summary job and returns the summary (or job handle).

Body:
```json
{
  "document_id": "doc_01J...",
  "length": "Medium",
  "style": "executive",
  "format": "bullets",
  "detail_level": "concise",
  "include_key_points": true,
  "include_quotes": false
}
```

Response:
- 202 Accepted: `{ "summary": Summary (status:"generating"), "job": ProcessingJob }`
- 404: document not found.
- 409: document not yet `ready`.

> The `ConfigureSummary` page collects `length`, `style`, `include_key_points`, `include_quotes`; the `ExtractedText` page collects `format` and `detail_level`. All five must be sent in one call.

#### `GET /api/v1/summaries` — library listing
Query params:
| param | values |
|---|---|
| `tab` | `all` \| `recent` \| `favorites` |
| `q` | free-text (matches title, excerpt, source) |
| `category` | Category |
| `format` | DocFormat |
| `length` | SummaryLength |
| `style` | SummaryStyle |
| `sort` | `created_at` \| `title` (default `created_at`) |
| `page`, `per_page` | pagination |

- 200: paginated `Summary[]` (each with all fields from §2.4).
- Powers `/summaries` (grid), the Dashboard "Recent summaries" (client requests top 3), and `/recent`/`/favorites`.

#### `GET /api/v1/summaries/:id`
- 200: `Summary`
- 404.

#### `POST /api/v1/summaries/:id/regenerate`
Re-run generation using stored `params` (or overrides in body).
- Body (optional): `{ "length"?, "style"?, "format"?, "detail_level"?, "include_key_points"?, "include_quotes"? }`
- 202: `{ "summary": Summary, "job": ProcessingJob }`

#### `DELETE /api/v1/summaries/:id`
- 204.

#### `POST /api/v1/summaries/:id/favorite` — toggle favorite
- 200: `{ "favorite": boolean }`

#### `GET /api/v1/summaries/:id/download` — download summary
- Query: `?format=pdf|markdown|txt` (default `markdown`)
- 200: binary download of the rendered summary.

#### `POST /api/v1/summaries/:id/share` — create share link
- 200: `{ "share_url": "https://app.summarist.ai/share/tok_01J...", "token": "tok_01J...", "expires_at": "2026-08-29T14:45:00Z" | null }`

#### `GET /api/v1/share/:token` — public read-only view
- 200: public projection of `Summary` (no auth required).

#### `GET /api/v1/summaries/:id/audio` — TTS ("Listen")
- Query: `?voice=default`
- Response (two-phase):
  - If not yet generated → `409` with `{ "status": "generating", "job_id": "job_..." }`; client polls `GET /api/v1/summaries/:id/audio/status`.
  - If ready → `200`: `{ "audio_url": "https://cdn.../sum_01J...mp3", "duration_seconds": 135, "voice": "default" }`
- The UI shows a player with a duration label (`2:15`). `duration_seconds` must be returned.

#### `GET /api/v1/summaries/:id/audio/status`
- 200: `{ "status": "generating" | "ready", "audio_url"?, "duration_seconds"? }`

---

### 3.5 Categories & metadata

#### `GET /api/v1/categories`
- 200: `{ "categories": ["Research", "Finance", "Tech", "Internal"] }`

#### `GET /api/v1/meta/options` — static options (optional; frontend currently hardcodes these)
- 200:
```json
{
  "lengths": ["Short", "Medium", "Long"],
  "styles": [
    { "value": "executive", "label": "Executive Summary", "description": "High-level overview focusing on main conclusions and decisions." },
    { "value": "key_points", "label": "Key Points", "description": "Bullet-point list extracting the most critical facts." },
    { "value": "detailed", "label": "Detailed Summary", "description": "Comprehensive breakdown preserving structural flow." },
    { "value": "study_notes", "label": "Study Notes", "description": "Optimized for learning and memorization." },
    { "value": "action_items", "label": "Action Items", "description": "Extracts tasks, deadlines, and responsibilities." }
  ],
  "formats": ["PDF", "DOC", "DOCX", "PPTX", "TXT", "WEB"],
  "detail_levels": ["concise", "medium", "detailed"]
}
```

---

### 3.6 Jobs & async processing

The processing pipeline is asynchronous. Two delivery mechanisms are required:

#### `GET /api/v1/jobs/:id` — poll status
- 200: `ProcessingJob`

#### `GET /api/v1/jobs/:id/stream` — Server-Sent Events (recommended)
Emits events; client subscribes on `/processing`:
```
event: stage
data: { "stage": "understanding", "stage_index": 2, "progress": 60 }

event: complete
data: { "document_id": "doc_...", "summary_id": "sum_..." }

event: error
data: { "error": { "code": "EXTRACTION_FAILED", "message": "..." } }
```

> Fallback if SSE is not desired: the frontend polls `GET /api/v1/documents/:id/status`.

#### `POST /api/v1/jobs/:id/cancel` — "Cancel processing"
- 200: `{ "status": "cancelled" }`
- Marks the job and document `cancelled`; deletes partial artifacts.

#### `POST /api/v1/jobs/:id/background` — "Run in background"
- 200: `{ "status": "running" }`
- Detaches the job from the client (keeps running server-side; the client navigates away). No-op if already running.

---

## 4. Processing pipeline (backend implementation)

```
upload/from-url
      │
      ▼
[uploaded]  store file, validate, create Document
      │
      ▼
[extracting]  parse layout + OCR (images/PDF) → ExtractedText
      │        • PDF/DOC/DOCX/PPTX/TXT: native text layer or OCR fallback
      │        • PNG/JPG/JPEG: OCR (sets ocr_method = "Advanced Vision V4")
      │        • WEB: readability extraction of main article content
      │        • compute pages, words, language (auto-detect)
      ▼
[understanding]  semantic analysis, key entities, sectioning (AI pass #1)
      │
      ▼
[preparing]  run LLM summarization with user params (AI pass #2)
      │
      ▼
[ready]  persist Summary; emit complete
```

### Summary generation contract (AI output must conform to §2.4)

The LLM prompt must return exactly the fields the UI renders:
- `tldr` (Quick Summary, drop-cap paragraph)
- `takeaways[]` (Key Takeaways grid — **when `include_key_points: true`**; otherwise empty array)
- `sections[]` (Detailed Analysis; `format: bullets|paragraph` and `detail_level` control density)
- `highlight` (Notable Quote — **when `include_quotes: true`**; otherwise `null`)
- `excerpt` (1–2 sentence subtitle)
- `category` (auto-classified)

---

## 5. Storage & infrastructure

| Concern | Recommendation |
|---|---|
| Object storage | S3-compatible (original files, extracted TXT, TTS audio, exported summaries). Signed URLs for download/audio. |
| Metadata DB | PostgreSQL. Tables: `users`, `documents`, `extracted_texts`, `summaries`, `jobs`. |
| Job queue | Redis + a worker (BullMQ / Celery / Sidekiq). Jobs: `extract`, `understand`, `summarize`, `tts`. |
| LLM | Any LLM API; enforce JSON-schema output for §2.4. |
| OCR | Tesseract / cloud vision API; record engine in `ocr_method`. |
| TTS | Cloud TTS (ElevenLabs / AWS Polly / Google TTS). |
| Cache | Redis for recent summaries list & share tokens. |
| Search | Postgres FTS or Elasticsearch for library + in-text search. |

---

## 6. Error codes

| HTTP | `code` | Meaning |
|---|---|---|
| 400 | `VALIDATION_ERROR` | malformed body/params |
| 401 | `UNAUTHENTICATED` | missing/invalid token |
| 403 | `FORBIDDEN` | not owner of resource |
| 404 | `NOT_FOUND` | resource missing |
| 409 | `CONFLICT` | resource in wrong state (e.g. doc not ready) |
| 409 | `JOB_ALREADY_RUNNING` | duplicate generation |
| 413 | `FILE_TOO_LARGE` | > 50 MB |
| 415 | `UNSUPPORTED_TYPE` | disallowed mime |
| 422 | `INVALID_URL` | from-url failure |
| 422 | `EXTRACTION_FAILED` | OCR/parse error |
| 429 | `RATE_LIMITED` | quota exceeded |
| 500 | `INTERNAL` | server error |
| 502 | `UPSTREAM_ERROR` | LLM/OCR/TTS provider failure |

---

## 7. AuthN / AuthZ notes

- All `/api/v1/*` routes except `POST /auth/*` and `GET /share/:token` require a valid Bearer token.
- Every resource is scoped to the owning `user_id`; cross-user access returns `404` (not `403`) to avoid enumeration.
- File uploads enforce per-user storage quota; the 50 MB cap is per file.

---

## 8. Frontend ↔ endpoint traceability

| Frontend location | Requires |
|---|---|
| `Dashboard.tsx` (Recent summaries) | `GET /summaries?tab=recent&per_page=3` |
| `Dashboard.tsx` (dropzone / Choose File) | `POST /documents` (multipart) |
| `Processing.tsx` (steps, cancel, background) | `GET /jobs/:id/stream`, `POST /jobs/:id/cancel`, `POST /jobs/:id/background` |
| `ExtractedText.tsx` | `GET /documents/:id/extracted-text`, `GET /documents/:id/search`, `GET /documents/:id/export.txt` |
| `ExtractedText.tsx` (properties) | fields in `ExtractedText` (format, ocr_method, words, pages, language) |
| `ConfigureSummary.tsx` | `POST /summaries` (length, style, include_key_points, include_quotes) |
| `Summary.tsx` (view) | `GET /summaries/:id` |
| `Summary.tsx` (actions) | `POST /summaries/:id/regenerate`, `/download`, `/favorite`, `/share`, `/audio` |
| `Summary.tsx` (View extracted text) | `GET /documents/:id/extracted-text` |
| `MySummaries.tsx` (tabs) | `GET /summaries?tab=all|recent|favorites` |
| `Sidebar.tsx` / `BottomNav.tsx` | `GET /summaries`, `GET /documents` (counts optional) |
| `TopBar.tsx` (Search the library) | `GET /summaries?q=...` |
| `Sidebar.tsx` (user footer) | `GET /me` |
| `EmptyState.tsx` (recent/favorites) | `GET /documents` / `GET /summaries?tab=favorites` |
| `settings` / `profile` pages | `GET /me/settings`, `PATCH /me/settings`, `PATCH /me` |

---

## 9. Open questions for implementation

1. **Async vs sync summary**: The `/processing` page implies a background job + streaming. If summaries are fast enough (<2 s), `POST /summaries` could return the final summary synchronously (200) and `/processing` becomes a transition only. Confirm target latency.
2. **`date` field formatting**: Confirm whether the backend returns a pre-formatted relative string or the client formats a timestamp.
3. **Category source**: confirm auto-classification vs user-selectable on the configure page (currently not in the UI).
4. **Auth provider**: email/password vs SSO (Google/Apple). The UI shows no login screen — assume a session is established before the SPA loads (e.g. cookie or injected token).
5. **Share**: public link vs logged-in-only.
6. **Plan/quotas**: free vs paid limits on uploads/summaries/TTS minutes.
