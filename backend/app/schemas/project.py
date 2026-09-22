from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import (
    ProjectStatus,
    ProjectVisibility,
)


# -----------------------------
# Base Schema
# -----------------------------
class ProjectBase(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    visibility: ProjectVisibility = (
        ProjectVisibility.PRIVATE
    )


# -----------------------------
# Create Project
# -----------------------------
class ProjectCreate(ProjectBase):
    workspace_id: UUID


# -----------------------------
# Update Project
# -----------------------------
class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)

    description: str | None = None

    visibility: ProjectVisibility | None = None

    status: ProjectStatus | None = None


# -----------------------------
# Project Summary
# -----------------------------
class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: ProjectStatus
    visibility: ProjectVisibility


# -----------------------------
# Full Response
# -----------------------------
class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    created_by: UUID

    status: ProjectStatus

    created_at: datetime
    updated_at: datetime