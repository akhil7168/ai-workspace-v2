from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.session import UserSession
from app.repositories.session_repository import SessionRepository
from app.core.security import create_refresh_token

class SessionService:

    def __init__(self, db):
        self.db = db
        self.repo = SessionRepository(db)

    def create_session(
        self,
        user_id: UUID,
        user_agent: str,
        ip_address: str,
    ) -> UserSession:

        refresh_token = create_refresh_token(subject=str(user_id))

        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            is_revoked=False,
        )

        self.repo.create(session)
        return session

    def validate_refresh_token(self, refresh_token: str):
        session = self.repo.get_by_refresh_token(refresh_token)

        if not session:
            return None

        if session.is_revoked:
            return None

        if session.expires_at < datetime.now(timezone.utc):
            return None

        return session

    def rotate_refresh_token(self, old_token: str):

        session = self.validate_refresh_token(old_token)

        if not session:
            return None

        new_token = create_refresh_token(subject=str(session.user_id))

        self.repo.update_refresh_token(session, new_token)

        return new_token

    def revoke_session(self, refresh_token: str):

        session = self.repo.get_by_refresh_token(refresh_token)

        if session:
            self.repo.revoke(session)

    def revoke_all_sessions(self, user_id: UUID):
        self.repo.revoke_all_user_sessions(user_id)