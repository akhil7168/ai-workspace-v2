from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt

from app.core.config import settings


def test_invalid_login_is_rejected(client):
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_invalid_form_login_is_rejected_with_validation_error(client):
    response = client.post(
        "/auth/login",
        data={"username": "not-an-email", "password": "Password123"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Email and password are required"


def test_form_login_supports_oauth2_password_fields(client, authenticated_user):
    account = authenticated_user()
    response = client.post(
        "/auth/login",
        data={
            "username": account["credentials"]["email"],
            "password": account["credentials"]["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_registration_login_and_current_user(client, authenticated_user):
    account = authenticated_user()

    assert account["tokens"]["token_type"] == "bearer"
    assert account["user"]["email"] == account["credentials"]["email"]

    for endpoint in ("/auth/me", "/users/me"):
        response = client.get(endpoint, headers=account["headers"])
        assert response.status_code == 200
        assert response.json()["id"] == account["user"]["id"]


def test_auth_me_rejects_missing_malformed_and_expired_access_tokens(
    client,
    authenticated_user,
):
    account = authenticated_user()
    assert client.get("/auth/me").status_code == 401

    malformed = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-token"},
    )
    assert malformed.status_code == 401

    valid_payload = jwt.decode(
        account["tokens"]["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    expired_token = jwt.encode(
        {
            "sub": valid_payload["sub"],
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    expired = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired.status_code == 401


def test_registration_rejects_invalid_fields_and_duplicate_email(
    client,
    authenticated_user,
):
    invalid = client.post(
        "/auth/register",
        json={
            "full_name": "A",
            "email": "not-an-email",
            "password": "short",
        },
    )
    assert invalid.status_code == 422

    account = authenticated_user()
    duplicate = client.post("/auth/register", json=account["credentials"])

    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"


def test_refresh_rotation_rejects_reuse_and_logout_revokes_token(
    client,
    authenticated_user,
):
    account = authenticated_user()
    original = account["tokens"]["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": original})
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()
    assert new_tokens["refresh_token"] != original
    assert new_tokens["access_token"]

    reused = client.post("/auth/refresh", json={"refresh_token": original})
    assert reused.status_code == 401

    logout = client.post(
        "/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert logout.status_code == 200
    assert logout.json() == {"message": "Logged out successfully"}

    after_logout = client.post(
        "/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert after_logout.status_code == 401


def test_logout_all_revokes_every_session_for_current_user(
    client,
    authenticated_user,
):
    account = authenticated_user()
    credentials = account["credentials"]
    second_login = client.post(
        "/auth/login",
        json={
            "email": credentials["email"],
            "password": credentials["password"],
        },
    )
    assert second_login.status_code == 200

    response = client.post("/auth/logout-all", headers=account["headers"])

    assert response.status_code == 200
    assert response.json()["revoked_sessions"] == 2
    for token in (
        account["tokens"]["refresh_token"],
        second_login.json()["refresh_token"],
    ):
        refresh = client.post("/auth/refresh", json={"refresh_token": token})
        assert refresh.status_code == 401


def test_invalid_refresh_and_logout_tokens_are_rejected(client):
    invalid_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": f"invalid-{uuid4()}"},
    )
    invalid_logout = client.post(
        "/auth/logout",
        json={"refresh_token": f"invalid-{uuid4()}"},
    )

    assert invalid_refresh.status_code == 401
    assert invalid_logout.status_code == 401
