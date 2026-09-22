from app.db.session import SessionLocal
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate

db = SessionLocal()

service = ProjectService(db)

payload = ProjectCreate(
    name="Stock Predictor V2",
    description="LSTM + RNN project",
)

project = service.create_project(
    workspace_id="YOUR_WORKSPACE_UUID",
    user_id="YOUR_USER_UUID",
    payload=payload,
)

print(project.id)
print(project.name)
print(project.workspace_id)