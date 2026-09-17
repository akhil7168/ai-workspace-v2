from datetime import datetime, timezone

from app.models.session import Session as UserSession
from app.repositories.session_repository import SessionRepository
from app.core.security import (
    create_access_token,
    create_refresh_token,
    refresh_token_expiry,
)

class SessionService:

    def __init__(self, db):
        self.repo = SessionRepository(db)

    # --------------------------------
    # Create new session
    # --------------------------------
    def create_session(
        self,
        user_id,
        user_agent=None,
        ip_address=None,
    ):
        refresh = create_refresh_token()

        session = UserSession(
            user_id=user_id,
            refresh_token=refresh,
            expires_at=refresh_token_expiry(),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.repo.create(session)

        return session

    # --------------------------------
    # Validate refresh token
    # --------------------------------
    def validate_refresh_token(self, refresh_token):

        session = self.repo.get_by_token(refresh_token)

        if not session:
            return None

        if session.is_revoked:
            return None

        if session.expires_at < datetime.now(timezone.utc):
            return None

        return session

    # --------------------------------
    # Revoke session
    # --------------------------------
    def revoke_session(self, refresh_token):
        session = self.repo.get_by_token(refresh_token)

        if session:
            self.repo.revoke(session)

    # --------------------------------
    # Revoke all sessions
    # --------------------------------
    def revoke_all_sessions(self, user_id):
        self.repo.revoke_all(user_id)

    # --------------------------------
    # Rotate Refresh Token
    # --------------------------------
    def rotate_refresh_token(self, refresh_token):

        session = self.validate_refresh_token(refresh_token)

        if session is None:
            return None

        session.is_revoked = True
        self.repo.update(session)

        return self.create_session(
            user_id=session.user_id,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )

    def refresh_access_token(self, refresh_token: str):

        new_session = self.rotate_refresh_token(refresh_token)

        if new_session is None:
            return None

        access_token = create_access_token(str(new_session.user_id))

        return {
            "access_token": access_token,
            "refresh_token": new_session.refresh_token,
            "token_type": "bearer",
        }

    def logout(self, refresh_token: str):

        session = self.validate_refresh_token(refresh_token)

        if session is None:
            return False

        self.repo.revoke(session)

        return True