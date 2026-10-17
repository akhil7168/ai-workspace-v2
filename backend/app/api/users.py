# FastAPI is provided by the backend environment.
# pyright: reportMissingImports=false
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import (
    get_current_active_user,
    require_roles,
)
from app.db.session import get_db
from app.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    PasswordUpdate,
)
from app.schemas.common import (
    AdminWelcomeResponse,
    ErrorResponse,
    MessageResponse,
)
from app.services.user_service import UserService
from app.models.user import User, UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ------------------------------------------------
# GET /users/me
# ------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
    },
)
def get_me(
    current_user=Depends(get_current_active_user),
):
    return current_user


# ------------------------------------------------
# GET /users/profile
# ------------------------------------------------

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get the current user's profile",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
    },
)
def get_profile(
    current_user=Depends(get_current_active_user),
):
    return current_user


# ------------------------------------------------
# PUT /users/profile
# ------------------------------------------------

@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update the current user's profile",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = UserService(db)

    return service.update_profile(
        current_user.id,
        payload,
    )


# ------------------------------------------------
# PATCH /users/password
# ------------------------------------------------

@router.patch(
    "/password",
    response_model=MessageResponse,
    summary="Change the current user's password",
    responses={
        400: {"model": ErrorResponse, "description": "The current password is incorrect."},
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The authenticated user is inactive."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
)
def update_password(
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = UserService(db)

    return service.update_password(
        current_user.id,
        payload,
    )

# ----------------------------------------------------
# ADMIN DEMO API
# ----------------------------------------------------

@router.get(
    "/admin-only",
    response_model=AdminWelcomeResponse,
    summary="Access the administrator-only example",
    description="Requires an active account with the global ADMIN user role.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "An active administrator account is required."},
    },
)
def admin_route(
    current_user=Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return {
        "message": "Welcome Admin!",
        "email": current_user.email,
    }

@router.get(
    "/all",
    response_model=list[UserResponse],
    summary="List all users",
    description="Administrator-only list of public user profiles; password hashes are not returned.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "An active administrator account is required."},
    },
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return UserService(db).get_all_users()