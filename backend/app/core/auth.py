from fastapi import Depends, HTTPException, status  # type: ignore[import-not-found]
from fastapi.security import OAuth2PasswordBearer  # type: ignore[import-not-found]
from typing import Any

from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Any = Depends(get_db),
):
    """
    Decode JWT token and return authenticated user.
    """

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid",
        )

    repository = UserRepository(db)

    user = repository.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_roles(*allowed_roles: str):
    """
    RBAC dependency.
    Usage:
        Depends(require_roles("ADMIN"))
        Depends(require_roles("ADMIN", "USER"))
    """

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker


def require_admin():
    """
    Convenience dependency for admin-only endpoints.
    """

    return require_roles("ADMIN")