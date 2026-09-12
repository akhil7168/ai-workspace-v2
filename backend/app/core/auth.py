from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from jose import JWTError

from sqlalchemy.orm import Session
from typing import Callable

from app.models.user import UserRole

from app.db.session import get_db
from app.services.token_service import TokenService
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# --------------------------------------------------
# Decode Access Token
# --------------------------------------------------

def get_current_user_payload(
    token: str = Depends(oauth2_scheme)
):

    payload = TokenService.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# --------------------------------------------------
# Get Current User Object
# --------------------------------------------------

def get_current_user(
    payload=Depends(get_current_user_payload),
    db: Session = Depends(get_db)
):

    repository = UserRepository(db)

    user = repository.get_by_email(payload["email"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found."
        )

    return user

# ----------------------------------------------------
# Role Authorization Dependency
# ----------------------------------------------------

def require_roles(
    *allowed_roles: UserRole,
) -> Callable:

    def dependency(
        current_user=Depends(get_current_user),
    ):

        if current_user.role not in [
            role.value for role in allowed_roles
        ]:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return dependency