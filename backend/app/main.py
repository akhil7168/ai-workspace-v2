from fastapi import FastAPI  # pyright: ignore[reportMissingImports]

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.health import router as health_router
from app.api.workspace import router as workspace_router
from app.api.project import router as project_router

app = FastAPI(
    title="AI Workspace V2 Backend",
    version="0.2.0",
    description="""
Production-ready authentication backend.

Features:
- JWT Authentication
- Refresh Tokens
- Protected APIs
- RBAC Authorization
""",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspace_router)
app.include_router(project_router)


@app.get("/")
def root():
    return {
        "message": "AI Workspace V2 Backend Running"
    }