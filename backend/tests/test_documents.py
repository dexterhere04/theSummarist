"""Document upload / extraction / search endpoint tests."""
from __future__ import annotations

from app.services.pipeline import run_job
from tests.conftest import SAMPLE_TXT


async def _upload(client, headers, name="qbr.txt", run_summary="false"):
    res = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": (name, SAMPLE_TXT.encode(), "text/plain")},
        data={"run_summary": run_summary},
    )
    assert res.status_code == 202, res.text
    return res.json()


async def test_upload_rejects_unsupported_type(client, auth_headers):
    res = await client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("x.exe", b"MZ...", "application/x-msdownload")},
    )
    assert res.status_code == 415
    assert res.json()["error"]["code"] == "UNSUPPORTED_TYPE"


async def test_upload_extract_and_artifacts(client, auth_headers):
    data = await _upload(client, auth_headers)
    doc, job = data["document"], data["job"]

    assert doc["status"] == "uploaded"
    assert doc["format"] == "TXT"
    assert job["type"] == "extract"
    assert job["total_stages"] == 4

    await run_job(job["id"])

    status = (
        await client.get(f"/api/v1/documents/{doc['id']}/status", headers=auth_headers)
    ).json()
    assert status["status"] == "succeeded"
    assert status["progress"] == 100

    detail = await client.get(f"/api/v1/documents/{doc['id']}", headers=auth_headers)
    assert detail.json()["status"] == "ready"
    assert detail.json()["words"] > 0

    et_res = await client.get(
        f"/api/v1/documents/{doc['id']}/extracted-text", headers=auth_headers
    )
    assert et_res.status_code == 200
    et = et_res.json()
    assert et["file_name"] == "qbr.txt"
    assert et["ocr_method"]
    assert et["body"][0]["paragraphs"]

    search = await client.get(
        f"/api/v1/documents/{doc['id']}/search",
        params={"q": "revenue"},
        headers=auth_headers,
    )
    assert search.status_code == 200
    body = search.json()
    assert body["total"] >= 1
    match = body["matches"][0]
    assert set(match) == {"section_heading", "paragraph_index", "snippet", "start", "end"}

    export = await client.get(
        f"/api/v1/documents/{doc['id']}/export.txt", headers=auth_headers
    )
    assert export.status_code == 200
    assert "Revenue grew strongly" in export.text

    download = await client.get(
        f"/api/v1/documents/{doc['id']}/download", headers=auth_headers
    )
    assert download.status_code == 200
    assert download.content.decode().startswith("Quarterly")


async def test_extracted_text_conflicts_before_ready(client, auth_headers):
    data = await _upload(client, auth_headers)
    doc_id = data["document"]["id"]
    res = await client.get(
        f"/api/v1/documents/{doc_id}/extracted-text", headers=auth_headers
    )
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "CONFLICT"


async def test_document_list_pagination_and_search(client, auth_headers):
    for i in range(3):
        await _upload(client, auth_headers, name=f"qbr{i}.txt")

    page1 = await client.get(
        "/api/v1/documents", params={"per_page": 2, "page": 1}, headers=auth_headers
    )
    body = page1.json()
    assert len(body["items"]) == 2
    assert body["total"] == 3
    assert body["has_more"] is True

    filtered = await client.get(
        "/api/v1/documents", params={"q": "qbr0"}, headers=auth_headers
    )
    assert filtered.json()["total"] == 1


async def test_delete_document_soft_deletes(client, auth_headers):
    data = await _upload(client, auth_headers)
    doc_id = data["document"]["id"]
    res = await client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert res.status_code == 204
    res = await client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert res.status_code == 404


async def test_cross_user_access_is_404(client, auth_headers):
    data = await _upload(client, auth_headers)
    doc_id = data["document"]["id"]

    await client.post(
        "/api/v1/auth/register",
        json={"email": "other@x.io", "password": "supersecret1", "name": "Other"},
    )
    other_login = await client.post(
        "/api/v1/auth/login", json={"email": "other@x.io", "password": "supersecret1"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    res = await client.get(f"/api/v1/documents/{doc_id}", headers=other_headers)
    assert res.status_code == 404


async def test_from_url_validates_scheme(client, auth_headers):
    res = await client.post(
        "/api/v1/documents/from-url",
        headers=auth_headers,
        json={"url": "ftp://nope.example.com"},
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_URL"
