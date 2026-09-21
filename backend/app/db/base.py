# backend/app/db/base.py

from app.db.session import Base

# Import all models so Alembic sees them.
from app.models.user import User
from app.models.session import Session
from app.models.workspace import Workspace
