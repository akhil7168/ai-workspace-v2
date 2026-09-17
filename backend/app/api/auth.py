from fastapi import APIRouter, Depends, HTTPException  # type: ignore[import-not-found]
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore[import-not-found]
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin,RefreshTokenRequest,RefreshTokenResponse, LogoutRequest
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService
from app.services.session_service import SessionService

from fastapi import Request  # type: ignore[import-not-found]


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    payload = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    return AuthService(db).login(
        payload,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host,
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


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
):
    success = SessionService(db).logout(
        payload.refresh_token
    )

    if not success:
        raise HTTPException(
            status_code=401,
            detail="Session already expired",
        )

    return {
        "message": "Logged out successfully"
    }

