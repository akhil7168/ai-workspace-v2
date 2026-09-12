from fastapi import APIRouter, Depends  # type: ignore[reportMissingImports]
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(payload)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    payload = UserLogin(
        email=form_data.username,   # username field contains email
        password=form_data.password,
    )

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