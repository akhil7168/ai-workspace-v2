from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_current_user():

    email = f"{uuid4()}@example.com"
    password = "Password123"

    client.post(
        "/auth/register",
        json={
            "full_name": "Protected User",
            "email": email,
            "password": password
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == email