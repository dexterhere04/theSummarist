"""Auth + account endpoint tests."""
from __future__ import annotations

REGISTER = "/api/v1/auth/register"


async def test_register_returns_user_and_tokens(client):
    res = await client.post(
        REGISTER,
        json={"email": "a@b.io", "password": "supersecret1", "name": "A"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["user"]["email"] == "a@b.io"
    assert body["user"]["avatar_initials"] == "A"
    assert body["user"]["plan"] == "free"
    assert body["access_token"] and body["refresh_token"]


async def test_register_duplicate_email_conflicts(client):
    payload = {"email": "dup@b.io", "password": "supersecret1", "name": "D"}
    assert (await client.post(REGISTER, json=payload)).status_code == 201
    res = await client.post(REGISTER, json=payload)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "CONFLICT"


async def test_login_success_and_failure(client):
    await client.post(
        REGISTER, json={"email": "l@b.io", "password": "supersecret1", "name": "L"}
    )
    ok = await client.post(
        "/api/v1/auth/login", json={"email": "l@b.io", "password": "supersecret1"}
    )
    assert ok.status_code == 200

    bad = await client.post(
        "/api/v1/auth/login", json={"email": "l@b.io", "password": "wrong-pass"}
    )
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_refresh_rotates_tokens(client):
    reg = (
        await client.post(
            REGISTER,
            json={"email": "r@b.io", "password": "supersecret1", "name": "R"},
        )
    ).json()
    res = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": reg["refresh_token"]}
    )
    assert res.status_code == 200
    assert res.json()["access_token"]
    assert res.json()["refresh_token"] != reg["refresh_token"]

    invalid = await client.post("/api/v1/auth/refresh", json={"refresh_token": "nope"})
    assert invalid.status_code == 401


async def test_logout_204(client):
    reg = (
        await client.post(
            REGISTER,
            json={"email": "o@b.io", "password": "supersecret1", "name": "O"},
        )
    ).json()
    res = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": reg["refresh_token"]}
    )
    assert res.status_code == 204


async def test_me_requires_auth(client):
    res = await client.get("/api/v1/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_patch_me_and_settings(client, auth_headers):
    res = await client.patch(
        "/api/v1/me", headers=auth_headers, json={"name": "Renamed"}
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Renamed"
    assert res.json()["avatar_initials"] == "R"

    res = await client.get("/api/v1/me/settings", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["default_length"] == "Medium"
    assert res.json()["default_style"] == "executive"

    res = await client.patch(
        "/api/v1/me/settings", headers=auth_headers, json={"default_length": "Short"}
    )
    assert res.status_code == 200
    assert res.json()["default_length"] == "Short"

    res = await client.get("/api/v1/categories")
    assert res.status_code == 200
    assert res.json()["categories"] == ["Research", "Finance", "Tech", "Internal"]
