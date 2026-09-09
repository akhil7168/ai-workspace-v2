from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordUpdate,
)
from app.core.auth import require_roles
from app.models.user import UserRole

from app.services.user_service import UserService

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).get_me(current_user)


# ------------------------------------------------
# GET /users/profile
# ------------------------------------------------

@router.get(
    "/profile",
    response_model=UserResponse,
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).get_profile(current_user)


# ------------------------------------------------
# PUT /users/profile
# ------------------------------------------------

@router.put(
    "/profile",
    response_model=UserResponse,
)
def update_profile(
    profile: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).update_profile(
        current_user,
        profile,
    )


# ------------------------------------------------
# PATCH /users/password
# ------------------------------------------------

@router.patch("/password")
def change_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    UserService(db).change_password(
        current_user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    return {
        "message": "Password updated successfully."
    }

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