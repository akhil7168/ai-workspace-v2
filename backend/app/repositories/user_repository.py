from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """User database repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def get_by_id(self, user_id):
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def get_all(self):
        stmt = select(User).order_by(User.created_at.desc())
        return list(self.db.scalars(stmt))

    def update(self, user: User):
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()