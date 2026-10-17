from typing import Literal

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class MessageResponse(BaseModel):
    message: str


class LogoutAllResponse(BaseModel):
    message: str
    revoked_sessions: int


class AdminWelcomeResponse(BaseModel):
    message: str
    email: str


class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    database: Literal["connected", "disconnected"]
