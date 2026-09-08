from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.user import UserCreate

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse
)

from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService(db).register(payload)


@router.post(
    "/login",
    response_model=AuthResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    return AuthService(db).login(
        payload.email,
        payload.password
    )

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return AuthService(db).refresh_access_token(
        payload.refresh_token
    )