from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_user():

    email = f"{uuid4()}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "Password123"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == email

    assert "access_token" in body