
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.session import UserSession


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: UserSession) -> UserSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_refresh_token(self, token: str) -> UserSession | None:
        return (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token == token)
            .first()
        )

    def get_active_by_refresh_token(self, token: str) -> UserSession | None:
        return (
            self.db.query(UserSession)
            .filter(
                UserSession.refresh_token == token,
                UserSession.is_revoked.is_(False),
            )
            .first()
        )

    def rotate(
        self,
        session: UserSession,
        new_token: str,
        expires_at: datetime,
        now: datetime,
    ) -> UserSession | None:
        # Atomic conditional update prevents the same old token being
        # successfully rotated more than once.
        result = (
            self.db.query(UserSession)
            .filter(
                UserSession.id == session.id,
                UserSession.refresh_token == session.refresh_token,
                UserSession.is_revoked.is_(False),
                UserSession.expires_at > now,
            )
            .update(
                {
                    UserSession.refresh_token: new_token,
                    UserSession.expires_at: expires_at,
                },
                synchronize_session=False,
            )
        )

        if result != 1:
            self.db.rollback()
            return None

        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke(self, session: UserSession) -> UserSession:
        session.is_revoked = True
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_all_user_sessions(self, user_id: UUID) -> int:
        count = (
            self.db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_revoked.is_(False),
            )
            .update(
                {UserSession.is_revoked: True},
                synchronize_session=False,
            )
        )
        self.db.commit()
        return count
