from fastapi import HTTPException, status  # type: ignore[import-not-found]
from typing import Any


from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    refresh_token_expiry,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.services.session_service import SessionService


class AuthService:
    def __init__(self, db: Any):
        self.db = db
        self.user_repository = UserRepository(db)

    def register(self, payload: UserCreate):
        existing_user = self.user_repository.get_by_email(payload.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            is_active=True,
            is_verified=False,
            role="USER",
        )

        self.user_repository.create(user)

        return {"message": "User registered successfully."}

    def login(
        self,
        payload: UserLogin,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ):
        user = self.user_repository.get_by_email(payload.email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        access = create_access_token(str(user.id))

        session_service = SessionService(self.db)

        session = session_service.create_session(
            user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        return {
            "access_token": access,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
        }