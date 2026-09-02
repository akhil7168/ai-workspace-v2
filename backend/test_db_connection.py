# test_db_connection.py

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())