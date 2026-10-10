
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.session_service import SessionService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            data = await request.json()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON request",
            )

        try:
            payload = UserLogin(**data)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password are required",
            )
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password are required",
            )

        payload = UserLogin(email=email, password=password)

    return AuthService(db).login(
        payload,
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    result = SessionService(db).rotate_refresh_token(payload.refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    session, new_refresh_token = result

    return {
        "access_token": create_access_token(str(session.user_id)),
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )

    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    count = SessionService(db).revoke_all_sessions(current_user.id)

    return {
        "message": "All sessions revoked",
        "revoked_sessions": count,
    }


@router.get("/me", response_model=UserResponse)
def get_auth_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user
