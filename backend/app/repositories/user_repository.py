from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------
    # Create User
    # -----------------------------------

    def create(self, user: User):

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    # -----------------------------------
    # Find by Email
    # -----------------------------------

    def get_by_email(self, email: str):

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    # -----------------------------------
    # Find by ID
    # -----------------------------------

    def get_by_id(self, user_id: str):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    # -----------------------------------
    # Update Profile
    # -----------------------------------

    def update_profile(
        self,
        user: User,
        full_name: str | None,
        email: str | None,
    ):

        if full_name is not None:
            user.full_name = full_name

        if email is not None:
            user.email = email

        self.db.commit()
        self.db.refresh(user)

        return user

    # -----------------------------------
    # Update Password
    # -----------------------------------

    def update_password(
        self,
        user: User,
        hashed_password: str,
    ):

        user.hashed_password = hashed_password

        self.db.commit()
        self.db.refresh(user)

        return user