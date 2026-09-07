from app.core.security import (
    hash_password,
    verify_password
)


def test_hash_password():

    password = "MySecurePassword123"

    hashed = hash_password(password)

    assert hashed != password

    assert verify_password(password, hashed)


def test_wrong_password():

    hashed = hash_password("CorrectPassword")

    assert verify_password(
        "WrongPassword",
        hashed
    ) is False