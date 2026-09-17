from uuid import uuid4

from app.db.session import SessionLocal
from app.services.session_service import SessionService

db = SessionLocal()

service = SessionService(db)

session = service.create_session(
    user_id=uuid4(),
    user_agent="Chrome",
    ip_address="127.0.0.1",
)

print("OLD TOKEN")
print(session.refresh_token)

rotated = service.rotate_refresh_token(
    session.refresh_token
)

print("\nNEW TOKEN")
print(rotated.refresh_token)

assert session.refresh_token != rotated.refresh_token

db.close()

print("\nRotation Test Passed")