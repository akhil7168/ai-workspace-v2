
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_refresh_token():
    email = f"{uuid4()}@example.com"
    password = "Password123"

    register = client.post(
        "/auth/register",
        json={
            "full_name": "Refresh User",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code in (200, 201), register.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    old_refresh_token = login.json()["refresh_token"]

    refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert refresh.status_code == 200, refresh.text

    tokens = refresh.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["refresh_token"] != old_refresh_token

    # A rotated refresh token must not be reusable.
    reuse = client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert reuse.status_code == 401, reuse.text
