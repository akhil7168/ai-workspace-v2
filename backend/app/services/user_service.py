from fastapi import HTTPException, status  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]
from uuid import UUID
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileUpdate, PasswordUpdate


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    # -------------------------
    # Update Profile
    # -------------------------
    def update_profile(
    self,
    user_id: UUID,
    payload: UserProfileUpdate,
):
        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if payload.full_name is not None:
            user.full_name = payload.full_name

        self.repository.db.commit()
        self.repository.db.refresh(user)

        return user

    # -------------------------
    # Update Password
    # -------------------------
    def update_password(
    self,
    user_id: UUID,
    payload: PasswordUpdate,
):
        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(
            payload.current_password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = hash_password(payload.new_password)

        self.repository.db.commit()

        return {
            "message": "Password updated successfully"
        }