
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.common import ErrorResponse, LogoutAllResponse, MessageResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.session_service import SessionService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a user",
    description="Create an account. Registration is public and returns the public user profile.",
    responses={
        400: {"model": ErrorResponse, "description": "Email is already registered."},
    },
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in",
    description=(
        "Authenticate with JSON email/password or form username/password "
        "(email is also accepted as the form username)."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": UserLogin.model_json_schema(),
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "format": "email"},
                            "email": {"type": "string", "format": "email"},
                            "password": {"type": "string"},
                        },
                        "required": ["password"],
                    },
                },
            },
        },
    },
    responses={
        400: {"model": ErrorResponse, "description": "Malformed JSON request."},
        401: {"model": ErrorResponse, "description": "Email or password is invalid."},
        422: {"model": ErrorResponse, "description": "Email and password are required or invalid."},
    },
)
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
        except ValidationError:
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

        try:
            payload = UserLogin(email=email, password=password)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password are required",
            )

    return AuthService(db).login(
        payload,
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token",
    description="Exchange a valid refresh token for a new access token and rotated refresh token.",
    responses={
        401: {"model": ErrorResponse, "description": "Refresh token is invalid, expired, or revoked."},
    },
)
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


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out a session",
    description="Revoke the session identified by the supplied refresh token; no bearer token is required.",
    responses={
        401: {"model": ErrorResponse, "description": "Refresh token is invalid or already revoked."},
    },
)
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


@router.post(
    "/logout-all",
    response_model=LogoutAllResponse,
    summary="Log out all sessions",
    description="Revoke every active refresh-token session belonging to the authenticated user.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
    },
)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    count = SessionService(db).revoke_all_sessions(current_user.id)

    return {
        "message": "All sessions revoked",
        "revoked_sessions": count,
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
    },
)
def get_auth_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user
