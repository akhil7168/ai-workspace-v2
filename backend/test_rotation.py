from app.db.session import SessionLocal
from app.models.user import User
from app.services.session_service import SessionService

db = SessionLocal()
service = SessionService(db)

user = db.query(User).filter(User.email == "akhil@example.com").first()

session, token = service.create_session(
    user_id=user.id,
    user_agent="Chrome",
    ip_address="127.0.0.1",
)

print("Old Token:", token[:25])

new_session, new_token = service.rotate_refresh_token(token)

print("Old Revoked:", service.repo.get_by_refresh_token(token).is_revoked)
print("New Token:", new_token[:25])