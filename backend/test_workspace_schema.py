from app.schemas.workspace import WorkspaceCreate

workspace = WorkspaceCreate(
    name="AI Workspace",
    description="Main AI projects",
)

print(workspace.model_dump())