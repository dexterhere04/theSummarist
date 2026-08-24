"""Summary lifecycle tests: generate, regenerate, favorite, share, audio, download."""
from __future__ import annotations

from app.services.pipeline import run_job
from tests.conftest import SAMPLE_TXT


async def _make_summary(client, headers, **overrides):
    up = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("qbr.txt", SAMPLE_TXT.encode(), "text/plain")},
        data={"run_summary": "false"},
    )
    doc = up.json()["document"]
    job = up.json()["job"]
    await run_job(job["id"])

    payload = {
        "document_id": doc["id"],
        "length": "Medium",
        "style": "executive",
        "format": "bullets",
        "detail_level": "concise",
        "include_key_points": True,
        "include_quotes": False,
    }
    payload.update(overrides)
    res = await client.post("/api/v1/summaries", headers=headers, json=payload)
    assert res.status_code == 202, res.text
    summary = res.json()["summary"]
    gen_job = res.json()["job"]
    await run_job(gen_job["id"])
    detail = await client.get(f"/api/v1/summaries/{summary['id']}", headers=headers)
    return doc, summary, detail.json()


async def test_generate_summary_full_shape(client, auth_headers):
    _, created, final = await _make_summary(
        client, auth_headers, include_quotes=True
    )

    assert created["status"] == "generating"
    for key in ("id", "document_id", "user_id", "title", "source", "format", "date",
                "length", "kind", "category", "tldr", "takeaways", "sections",
                "highlight", "favorite", "status", "params"):
        assert key in final, key

    assert final["status"] == "ready"
    assert final["kind"] == "Executive Summary"
    assert final["tldr"]
    assert final["highlight"]  # include_quotes=True
    assert {t["title"] and t["body"] for t in final["takeaways"]}
    assert final["params"] == {
        "format": "bullets",
        "detail_level": "concise",
        "include_key_points": True,
        "include_quotes": True,
    }
    assert final["date"].startswith("Today,")


async def test_toggles_honored(client, auth_headers):
    _, _, no_points = await _make_summary(
        client, auth_headers, include_key_points=False, include_quotes=False
    )
    assert no_points["takeaways"] == []
    assert no_points["highlight"] is None


async def test_create_summary_requires_ready_doc(client, auth_headers):
    up = await client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("q.txt", SAMPLE_TXT.encode(), "text/plain")},
        data={"run_summary": "false"},
    )
    doc_id = up.json()["document"]["id"]
    res = await client.post(
        "/api/v1/summaries",
        headers=auth_headers,
        json={
            "document_id": doc_id,
            "length": "Short",
            "style": "executive",
            "format": "bullets",
            "detail_level": "concise",
        },
    )
    assert res.status_code == 409


async def test_list_tabs_filters_and_pagination(client, auth_headers):
    await _make_summary(client, auth_headers)

    all_items = await client.get("/api/v1/summaries", headers=auth_headers)
    body = all_items.json()
    assert body["total"] >= 1
    item = body["items"][0]
    assert "date" in item and "kind" in item

    fav = await client.post(
        f"/api/v1/summaries/{item['id']}/favorite", headers=auth_headers
    )
    assert fav.json() == {"favorite": True}

    favorites = await client.get(
        "/api/v1/summaries", params={"tab": "favorites"}, headers=auth_headers
    )
    assert favorites.json()["total"] == 1

    filtered = await client.get(
        "/api/v1/summaries",
        params={"category": "Research"},
        headers=auth_headers,
    )
    assert filtered.json()["total"] == body["total"]

    searched = await client.get(
        "/api/v1/summaries", params={"q": "zzz-no-match"}, headers=auth_headers
    )
    assert searched.json()["total"] == 0


async def test_regenerate_updates_params_and_reruns(client, auth_headers):
    _, created, _ = await _make_summary(client, auth_headers)

    res = await client.post(
        f"/api/v1/summaries/{created['id']}/regenerate",
        headers=auth_headers,
        json={"style": "key_points", "include_quotes": True},
    )
    assert res.status_code == 202
    assert res.json()["summary"]["status"] == "generating"

    gen_job = res.json()["job"]
    await run_job(gen_job["id"])

    detail_res = await client.get(
        f"/api/v1/summaries/{created['id']}", headers=auth_headers
    )
    detail = detail_res.json()
    assert detail["status"] == "ready"
    assert detail["style"] == "key_points"
    assert detail["kind"] == "Key Points"
    assert detail["highlight"]
    assert detail["params"]["include_quotes"] is True


async def test_share_public_readonly(client, auth_headers):
    _, created, _ = await _make_summary(client, auth_headers)

    share = await client.post(
        f"/api/v1/summaries/{created['id']}/share", headers=auth_headers
    )
    assert share.status_code == 200
    token = share.json()["token"]
    assert share.json()["share_url"].endswith(f"/share/{token}")
    assert share.json()["expires_at"] is not None

    public = await client.get(f"/api/v1/share/{token}")
    assert public.status_code == 200
    assert public.json()["id"] == created["id"]

    missing = await client.get("/api/v1/share/not-a-real-token")
    assert missing.status_code == 404


async def test_audio_returns_stub_metadata(client, auth_headers):
    _, created, _ = await _make_summary(client, auth_headers)

    audio = await client.get(
        f"/api/v1/summaries/{created['id']}/audio",
        params={"voice": "default"},
        headers=auth_headers,
    )
    assert audio.status_code == 200
    body = audio.json()
    assert body["audio_url"].endswith(".mp3")
    assert body["duration_seconds"] >= 10
    assert body["voice"] == "default"

    status = await client.get(
        f"/api/v1/summaries/{created['id']}/audio/status", headers=auth_headers
    )
    assert status.json()["status"] == "ready"


async def test_download_markdown_txt_pdf(client, auth_headers):
    _, created, _ = await _make_summary(client, auth_headers)

    md = await client.get(
        f"/api/v1/summaries/{created['id']}/download",
        params={"format": "markdown"},
        headers=auth_headers,
    )
    assert md.status_code == 200
    assert "# " in md.text

    txt = await client.get(
        f"/api/v1/summaries/{created['id']}/download",
        params={"format": "txt"},
        headers=auth_headers,
    )
    assert txt.status_code == 200

    pdf = await client.get(
        f"/api/v1/summaries/{created['id']}/download",
        params={"format": "pdf"},
        headers=auth_headers,
    )
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF-")


async def test_delete_summary(client, auth_headers):
    _, created, _ = await _make_summary(client, auth_headers)
    res = await client.delete(f"/api/v1/summaries/{created['id']}", headers=auth_headers)
    assert res.status_code == 204
    res = await client.get(f"/api/v1/summaries/{created['id']}", headers=auth_headers)
    assert res.status_code == 404
