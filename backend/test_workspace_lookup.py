from app.db.session import SessionLocal
from app.repositories.workspace_repository import WorkspaceRepository

db = SessionLocal()

repo = WorkspaceRepository(db)

workspace = repo.get_by_id(
    "REPLACE_WITH_WORKSPACE_UUID"
)

print(workspace)