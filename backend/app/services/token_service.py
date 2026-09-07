from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings


class TokenService:

    @staticmethod
    def create_access_token(
        user_id: str,
        email: str
    ) -> str:

        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def create_refresh_token(
        user_id: str,
        email: str
    ) -> str:

        payload = {
            "sub": user_id,
            "email": email,
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str):

        try:

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            return payload

        except JWTError:
            return None