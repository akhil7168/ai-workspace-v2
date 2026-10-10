
from datetime import datetime, timezone
from uuid import UUID

from app.core.security import create_refresh_token, refresh_token_expiry
from app.models.session import UserSession
from app.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, db):
        self.db = db
        self.repo = SessionRepository(db)

    def create_session(
        self,
        user_id: UUID,
        refresh_token: str,
        user_agent: str = "",
        ip_address: str = "",
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=refresh_token_expiry(),
            is_revoked=False,
        )
        return self.repo.create(session)

    def get_by_refresh_token(self, refresh_token: str):
        return self.repo.get_by_refresh_token(refresh_token)

    def rotate_refresh_token(
        self,
        old_token: str,
    ) -> tuple[UserSession, str] | None:
        session = self.repo.get_active_by_refresh_token(old_token)

        if session is None:
            return None

        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        if expires_at <= now:
            self.repo.revoke(session)
            return None

        new_token = create_refresh_token(subject=str(session.user_id))

        try:
            updated_session = self.repo.rotate(
                session=session,
                new_token=new_token,
                expires_at=refresh_token_expiry(),
                now=now,
            )
        except Exception:
            self.db.rollback()
            raise

        if updated_session is None:
            return None

        return updated_session, new_token

    def revoke_session(self, refresh_token: str) -> bool:
        session = self.repo.get_active_by_refresh_token(refresh_token)

        if session is None:
            return False

        self.repo.revoke(session)
        return True

    def revoke_all_sessions(self, user_id: UUID) -> int:
        return self.repo.revoke_all_user_sessions(user_id)
