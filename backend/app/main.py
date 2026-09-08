from fastapi import FastAPI

from fastapi import Depends

from app.api.auth import router as auth_router


from app.core.auth import get_current_user_payload
from app.core.config import settings
from app.api.health import router as health_router

app = FastAPI(
    title="AI Workspace V2",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "AI Workspace V2 Backend Running"
    }


@app.get("/token-info")
def token_info(
    payload=Depends(get_current_user_payload)
):
    return payload