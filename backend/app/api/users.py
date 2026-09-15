# FastAPI is provided by the backend environment.
# pyright: reportMissingImports=false
from fastapi import APIRouter, Depends
from typing import Any

from app.core.auth import (
    get_current_user,
    require_roles,
)
from app.db.session import get_db
from app.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    PasswordUpdate,
)
from app.services.user_service import UserService
from app.models.user import UserRole

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
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user


# ------------------------------------------------
# GET /users/profile
# ------------------------------------------------

@router.get(
    "/profile",
    response_model=UserResponse,
)
def get_profile(
    current_user=Depends(get_current_user),
):
    return current_user


# ------------------------------------------------
# PUT /users/profile
# ------------------------------------------------

@router.put(
    "/profile",
    response_model=UserResponse,
)
def update_profile(
    payload: UserProfileUpdate,
    db: Any = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = UserService(db)

    return service.update_profile(
        current_user.id,
        payload,
    )


# ------------------------------------------------
# PATCH /users/password
# ------------------------------------------------

@router.patch("/password")
def update_password(
    payload: PasswordUpdate,
    db: Any = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = UserService(db)

    return service.update_password(
        current_user.id,
        payload,
    )

# ----------------------------------------------------
# ADMIN DEMO API
# ----------------------------------------------------

@router.get("/admin-only")
def admin_route(
    current_user=Depends(
        require_roles(UserRole.ADMIN)
    )
):
    return {
        "message": "Welcome Admin!",
        "email": current_user.email,
    }