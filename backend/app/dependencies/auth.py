from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

from fastapi import Depends, HTTPException, status

from app.core.security import decode_token

async def get_current_user_payload(
    token: str = Depends(oauth2_scheme),
):
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload