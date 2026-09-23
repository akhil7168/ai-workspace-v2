from uuid import UUID

from fastapi import Depends, HTTPException, status  # pyright: ignore[reportMissingImports]
from fastapi.security import OAuth2PasswordBearer  # pyright: ignore[reportMissingImports]
from jose import JWTError, jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -----------------------------
# Authentication
# -----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
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

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = UUID(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
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
def require_roles(*allowed_roles: str):
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