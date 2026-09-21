from fastapi import APIRouter, Depends, HTTPException  # type: ignore[import-not-found]
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore[import-not-found]
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin,RefreshTokenRequest,RefreshTokenResponse, LogoutRequest
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService
from app.services.session_service import SessionService
from app.core.security import create_access_token

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
@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    payload = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    user_agent = request.headers.get("user-agent", "")
    ip_address = request.client.host if request.client else ""

    return AuthService(db).login(
        payload,
        user_agent=user_agent,
        ip_address=ip_address,
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    result = SessionService(db).rotate_refresh_token(payload.refresh_token)

    if result is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session, new_refresh_token = result

    access_token = create_access_token(str(session.user_id))

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    success = SessionService(db).revoke_session(payload.refresh_token)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Logged out successfully"}

