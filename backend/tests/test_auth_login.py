from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_user():

    email = f"{uuid4()}@example.com"

    password = "Password123"

    client.post(
        "/auth/register",
        json={
            "full_name": "Login User",
            "email": email,
            "password": password
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"