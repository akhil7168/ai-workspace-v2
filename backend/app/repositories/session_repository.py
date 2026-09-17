from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DbSession  # type: ignore[import-not-found]

from app.models.session import Session as UserSession


class SessionRepository:

    def __init__(self, db: "DbSession"):
        self.db = db

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, session: UserSession):
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    # -----------------------------
    # READ
    # -----------------------------
    def get_by_token(self, refresh_token: str):
        return (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token == refresh_token)
            .first()
        )

    def get_by_id(self, session_id: UUID):
        return (
            self.db.query(UserSession)
            .filter(UserSession.id == session_id)
            .first()
        )

    def get_user_sessions(self, user_id: UUID):
        return (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .order_by(UserSession.created_at.desc())
            .all()
        )

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(self, session: UserSession):
        self.db.commit()
        self.db.refresh(session)
        return session

    # -----------------------------
    # DELETE
    # -----------------------------
    def revoke(self, session: UserSession):
        session.is_revoked = True
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_all(self, user_id: UUID):
        sessions = (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .all()
        )

        for session in sessions:
            session.is_revoked = True

        self.db.commit()