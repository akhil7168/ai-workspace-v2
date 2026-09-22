from typing import Any

from app.models.session import UserSession

class SessionRepository:

    def __init__(self, db: Any):
        self.db = db

    def create(self, session: UserSession):
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_refresh_token(self, token: str):
        return (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token == token)
            .first()
        )

    def revoke(self, session: UserSession):
        session.is_revoked = True
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_all_user_sessions(self, user_id):
        (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .update({"is_revoked": True})
        )

        self.db.commit()