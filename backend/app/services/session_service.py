from datetime import datetime, timedelta, timezone

from typing import Any

from app.models.session import Session as UserSession
from app.repositories.session_repository import SessionRepository
from app.core.security import create_refresh_token
from app.core.config import settings


class SessionService:

    def __init__(self, db: Any):
        self.repo = SessionRepository(db)

    def create_session(
        self,
        user_id,
        user_agent: str,
        ip_address: str,
    ):
        refresh_token = create_refresh_token()

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )

        return self.repo.create(session)

    def rotate_refresh_token(self, old_token: str):
        session = self.repo.get_by_refresh_token(old_token)

        if not session:
            return None

        if session.is_revoked:
            return None

        self.repo.revoke(session)

        return self.create_session(
            session.user_id,
            session.user_agent,
            session.ip_address,
        )

    def logout(self, refresh_token: str):
        session = self.repo.get_by_refresh_token(refresh_token)

        if session:
            self.repo.revoke(session)

        return True

    def logout_all(self, user_id):
        self.repo.revoke_all_user_sessions(user_id)
        return True