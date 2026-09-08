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
            "password": password
        }
    )

    refresh = register.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh
        }
    )

    assert response.status_code == 200

    assert "access_token" in response.json()