import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from jose import JWTError, jwt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    import jwt as jwt  # type: ignore[import-not-found]
    from jwt import InvalidTokenError as JWTError  # type: ignore[import-not-found]

from passlib.context import CryptContext  # type: ignore[import-not-found]

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ----------------------------
# Password Utilities
# ----------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# ----------------------------
# JWT Utilities
# ----------------------------

def create_access_token(subject: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | None = None):
    return secrets.token_urlsafe(64)


def decode_token(token: str):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    
def refresh_token_expiry():
    """
    Returns expiry timestamp for refresh token.
    """
    return datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )