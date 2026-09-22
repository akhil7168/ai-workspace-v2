from requests import session

from app.schemas import user
from fastapi import HTTPException, status  # type: ignore[import-not-found]
from typing import Any
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

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
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, payload: UserCreate):
        existing = self.user_repo.get_by_email(payload.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),   # ✅ FIXED
        )

        return self.user_repo.create(user)

    def login(self, payload, user_agent="", ip_address=""):
        user = self.db.query(User).filter(User.email == payload.email).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(str(user.id))

        session = SessionService(self.db).create_session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        refresh_token = session.refresh_token

        return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }