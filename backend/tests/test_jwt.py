from app.services.token_service import TokenService


def test_create_access_token():

    token = TokenService.create_access_token(
        "user123",
        "akhil@example.com"
    )

    payload = TokenService.decode_token(token)

    assert payload["sub"] == "user123"

    assert payload["email"] == "akhil@example.com"

    assert payload["type"] == "access"


def test_create_refresh_token():

    token = TokenService.create_refresh_token(
        "user123",
        "akhil@example.com"
    )

    payload = TokenService.decode_token(token)

    assert payload["type"] == "refresh"