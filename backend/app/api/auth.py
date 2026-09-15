from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore[import-not-found]
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService

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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    payload = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    # This is the ONLY valid call.
    return AuthService(db).login(payload)

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