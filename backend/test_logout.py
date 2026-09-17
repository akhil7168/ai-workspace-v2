from app.db.session import SessionLocal
from app.models.user import User
from app.services.session_service import SessionService

db = SessionLocal()

email = "logout_test@example.com"

user = db.query(User).filter(User.email == email).first()

if not user:
    user = User(
        full_name="Logout User",
        email=email,
        password_hash="dummy_hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

service = SessionService(db)

session = service.create_session(
    user.id,
    "Chrome",
    "127.0.0.1",
)

service.logout(session.refresh_token)

session = service.repo.get_by_refresh_token(session.refresh_token)

print("Revoked:", session.is_revoked)

db.close()