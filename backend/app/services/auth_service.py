from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.security import verify_password

from app.models.user import User

from app.repositories.user_repository import UserRepository

from app.schemas.user import UserCreate

from app.services.token_service import TokenService


class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    # ----------------------------
    # Register User
    # ----------------------------

    def register(self, payload: UserCreate):

        existing = self.repository.get_by_email(payload.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password)
        )

        created_user = self.repository.create(user)

        return {
            "user_id": str(created_user.id),
            "full_name": created_user.full_name,
            "email": created_user.email,
            "access_token": TokenService.create_access_token(
                str(created_user.id),
                created_user.email
            ),
            "refresh_token": TokenService.create_refresh_token(
                str(created_user.id),
                created_user.email
            ),
            "token_type": "bearer"
        }

    # ----------------------------
    # Login User
    # ----------------------------

    def login(
        self,
        email: str,
        password: str
    ):

        user = self.repository.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "access_token": TokenService.create_access_token(
                str(user.id),
                user.email
            ),
            "refresh_token": TokenService.create_refresh_token(
                str(user.id),
                user.email
            ),
            "token_type": "bearer"
        }

    # ----------------------------
    # Refresh Access Token
    # ----------------------------

    def refresh_access_token(
        self,
        refresh_token: str
    ):

        payload = TokenService.decode_token(refresh_token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required."
            )

        user = self.repository.get_by_email(payload["email"])

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        return {
            "access_token": TokenService.create_access_token(
                str(user.id),
                user.email
            ),
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }