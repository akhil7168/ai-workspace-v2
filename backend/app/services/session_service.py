from datetime import datetime, timedelta, timezone

from typing import Any

from app.models.session import UserSession
from app.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, db: Any):
        self.db = db
        self.repo = SessionRepository(db)

    # -----------------------------
    # Create Session
    # -----------------------------
    def create_session(
        self,
        user_id,
        refresh_token: str,
        user_agent: str,
        ip_address: str,
    ) -> UserSession:

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

    # -----------------------------
    # Get Session
    # -----------------------------
    def get_by_refresh_token(self, refresh_token: str):
        return self.repo.get_by_refresh_token(refresh_token)

    # -----------------------------
    # Rotate Refresh Token
    # -----------------------------
    def rotate_refresh_token(self, old_token: str, new_token: str):
        session = self.repo.get_by_refresh_token(old_token)

        if not session:
            return None

        session.refresh_token = new_token
        self.repo.update(session)

        return session

    # -----------------------------
    # Revoke Session
    # -----------------------------
    def revoke_session(self, refresh_token: str):
        session = self.repo.get_by_refresh_token(refresh_token)

        if session:
            session.is_revoked = True
            self.repo.update(session)

        return session

    # -----------------------------
    # Revoke All Sessions
    # -----------------------------
    def revoke_all_sessions(self, user_id):
        sessions = self.repo.get_user_sessions(user_id)

        for session in sessions:
            session.is_revoked = True
            self.repo.update(session)

        return len(sessions)