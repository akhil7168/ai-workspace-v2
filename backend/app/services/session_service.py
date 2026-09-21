from datetime import datetime, timedelta, timezone

from app.models.session import Session
from app.repositories.session_repository import SessionRepository
from app.core.security import create_refresh_token


class SessionService:
    def __init__(self, db):
        self.db = db
        self.repo = SessionRepository(db)

    def create_session(
        self,
        user_id,
        user_agent: str = "",
        ip_address: str = "",
    ):
        """
        Creates a DB session and generates a refresh token.
        Returns (session, refresh_token)
        """

        refresh_token = create_refresh_token(str(user_id))

        session = Session(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            is_revoked=False,
        )

        self.repo.create(session)

        return session, refresh_token

    def rotate_refresh_token(self, old_token: str):
        session = self.repo.get_by_refresh_token(old_token)

        if not session:
            return None

        if session.is_revoked:
            return None

        if session.expires_at < datetime.now(timezone.utc):
            return None

        session.is_revoked = True
        self.repo.update(session)

        new_session, new_token = self.create_session(
            user_id=session.user_id,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )

        return new_session, new_token

    def revoke_session(self, refresh_token: str):
        session = self.repo.get_by_refresh_token(refresh_token)

        if not session:
            return False

        session.is_revoked = True
        self.repo.update(session)

        return True