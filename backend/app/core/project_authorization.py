from uuid import UUID

from fastapi import Depends, HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.core.auth import get_current_user
from app.db.session import get_db
from app.services.project_service import ProjectService


def require_project_owner(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = ProjectService(db).get_project(
        project_id
    )

    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Project ownership required",
        )

    return project