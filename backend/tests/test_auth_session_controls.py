
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.main import app

client = TestClient(app)


def create_logged_in_user():
    email = f"{uuid4()}@example.com"
    password = "Password123"

    register = client.post(
        "/auth/register",
        json={
            "full_name": "Session Test User",
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

    return login.json()


def test_auth_me_requires_access_token():
    login = create_logged_in_user()

    unauthorized = client.get("/auth/me")
    assert unauthorized.status_code == 401

    authenticated = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert authenticated.status_code == 200, authenticated.text


def test_expired_access_token_is_rejected():
    login = create_logged_in_user()

    # The account exists, but the access token is already expired.
    # Obtain the user ID from a valid token's subject.
    valid_payload = jwt.decode(
        login["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    user_id = valid_payload["sub"]

    expired_token = jwt.encode(
        {
            "sub": user_id,
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_logout_revokes_refresh_token():
    login = create_logged_in_user()
    refresh_token = login["refresh_token"]

    logout = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout.status_code == 200, logout.text

    refresh_again = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_again.status_code == 401


def test_logout_all_revokes_all_refresh_tokens():
    first_login = create_logged_in_user()

    # A second login creates a second session for the same account.
    # Registering separately would test two accounts, not logout-all.
    email = f"{uuid4()}@example.com"
    password = "Password123"

    register = client.post(
        "/auth/register",
        json={
            "full_name": "Logout All User",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code in (200, 201), register.text

    first_session = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    second_session = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert first_session.status_code == 200, first_session.text
    assert second_session.status_code == 200, second_session.text

    access_token = first_session.json()["access_token"]
    first_refresh = first_session.json()["refresh_token"]
    second_refresh = second_session.json()["refresh_token"]

    response = client.post(
        "/auth/logout-all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["revoked_sessions"] >= 2

    for token in (first_refresh, second_refresh):
        refresh = client.post(
            "/auth/refresh",
            json={"refresh_token": token},
        )
        assert refresh.status_code == 401
