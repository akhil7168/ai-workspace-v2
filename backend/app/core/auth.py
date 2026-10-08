from uuid import UUID

from fastapi import Depends, HTTPException, status  # pyright: ignore[reportMissingImports]
from fastapi.security import OAuth2PasswordBearer  # pyright: ignore[reportMissingImports]
from jose import JWTError, jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# -----------------------------
# Authentication
# -----------------------------
def get_current_user_payload(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("sub") is None:
            raise credentials_exception

        return payload

    except JWTError:
        raise credentials_exception


def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )

    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# -----------------------------
# Active user dependency
# -----------------------------
def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Inactive user",
        )

    return current_user


# -----------------------------
# Role Based Access Control
# -----------------------------
def require_roles(*allowed_roles):
    """
    Usage:
        Depends(require_roles("admin"))
        Depends(require_roles("admin", "manager"))
    """

    def role_checker(
        current_user: User = Depends(get_current_active_user),
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
            )

        return current_user

    return role_checker
