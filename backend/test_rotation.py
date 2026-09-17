from app.db.session import SessionLocal
from app.models.user import User
from app.services.session_service import SessionService

db = SessionLocal()

email = "rotation_test@example.com"

user = db.query(User).filter(User.email == email).first()

if not user:
    user = User(
        full_name="Rotation User",
        email=email,
        password_hash="dummy_hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

service = SessionService(db)

session = service.create_session(
    user_id=user.id,
    user_agent="Chrome",
    ip_address="127.0.0.1",
)

new_session = service.rotate_refresh_token(session.refresh_token)

print("Old revoked:", service.repo.get_by_refresh_token(session.refresh_token).is_revoked)
print("New Token:", new_session.refresh_token[:25], "...")

db.close()