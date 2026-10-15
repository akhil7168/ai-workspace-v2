from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.token_service import TokenService


def test_access_token_contains_subject_and_access_type():
    payload = decode_token(create_access_token("user-123"))

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_invalid_and_malformed_access_tokens_are_rejected():
    for token in ("not-a-jwt", create_access_token("user-123") + "tampered"):
        with pytest.raises(JWTError):
            decode_token(token)


def test_expired_access_token_is_rejected():
    token = jwt.encode(
        {
            "sub": "user-123",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_token(token)


def test_refresh_tokens_are_opaque_and_unique():
    first = create_refresh_token(subject="user-123")
    second = create_refresh_token(subject="user-123")

    assert first != second
    with pytest.raises(JWTError):
        decode_token(first)


def test_password_hash_verifies_only_the_original_password():
    hashed = hash_password("correct-password")

    assert hashed != "correct-password"
    assert verify_password("correct-password", hashed)
    assert not verify_password("incorrect-password", hashed)


def test_legacy_token_service_decodes_access_and_refresh_claims():
    access = TokenService.create_access_token("user-123", "user@example.com")
    refresh = TokenService.create_refresh_token("user-123", "user@example.com")
    access_payload = TokenService.decode_token(access)

    assert access_payload["sub"] == "user-123"
    assert access_payload["email"] == "user@example.com"
    assert access_payload["type"] == "access"
    assert TokenService.decode_token(refresh)["type"] == "refresh"
    assert TokenService.decode_token("malformed-token") is None
