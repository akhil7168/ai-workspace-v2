from uuid import uuid4

from app.schemas.project import ProjectCreate

payload = ProjectCreate(
    workspace_id=uuid4(),
    title="Stock Predictor",
    description="LSTM forecasting project",
)

print(payload.model_dump())