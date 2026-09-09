from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_change_password():

    email = f"{uuid4()}@example.com"

    old_password = "Password123"

    new_password = "Password456"

    client.post(
        "/auth/register",
        json={
            "full_name": "Password User",
            "email": email,
            "password": old_password,
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    token = login.json()["access_token"]

    response = client.patch(
        "/users/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == 200

    failed_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )

    assert failed_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": new_password,
        },
    )

    assert new_login.status_code == 200