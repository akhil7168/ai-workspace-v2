from fastapi import APIRouter  # type: ignore[import-not-found]
from fastapi.responses import JSONResponse  # type: ignore[import-not-found]
from sqlalchemy import text  # type: ignore[import-not-found]

from app.db.session import engine
from app.schemas.common import HealthResponse


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Check API and database health",
    description="Returns healthy when a simple database query succeeds, otherwise unhealthy.",
    responses={
        503: {
            "model": HealthResponse,
            "description": "The database check failed.",
        },
    },
)
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )

    return {
        "status": "healthy",
        "database": "connected",
    }