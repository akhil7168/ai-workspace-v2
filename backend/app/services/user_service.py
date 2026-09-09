from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate
from app.core.security import verify_password, hash_password


class UserService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    # -----------------------------------
    # Current User
    # -----------------------------------

    def get_me(self, current_user: User):

        return current_user

    # -----------------------------------
    # Profile
    # -----------------------------------

    def get_profile(self, current_user: User):

        return current_user

    # -----------------------------------
    # Update Profile
    # -----------------------------------

    def update_profile(
        self,
        current_user: User,
        profile: UserUpdate,
    ):

        # Prevent duplicate email

        if (
            profile.email
            and profile.email != current_user.email
        ):

            existing = self.repository.get_by_email(
                profile.email
            )

            if existing:

                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered.",
                )

        return self.repository.update_profile(
            current_user,
            full_name=profile.full_name,
            email=profile.email,
        )

    # -----------------------------------
    # Change Password
    # -----------------------------------

    def change_password(
        self,
        current_user: User,
        current_password: str,
        new_password: str,
    ):

        if not verify_password(
            current_password,
            current_user.hashed_password,
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect.",
            )

        hashed = hash_password(new_password)

        return self.repository.update_password(
            current_user,
            hashed,
        )