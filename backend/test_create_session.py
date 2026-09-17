from app.db.session import SessionLocal
from app.models.user import User
from app.services.session_service import SessionService
from app.core.security import hash_password

db = SessionLocal()

# --------------------------------------------------
# Step 1 — Create a temporary test user
# --------------------------------------------------

email = "session_test@example.com"

user = db.query(User).filter(User.email == email).first()

if not user:
    user = User(
        full_name="Session Test User",
        email=email,
        password_hash=hash_password("Password@123"),
        role="user",
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

print("Test User:", user.id)

# --------------------------------------------------
# Step 2 — Create Session
# --------------------------------------------------

service = SessionService(db)

session = service.create_session(
    user_id=user.id,
    refresh_token="sample_refresh_token_123456",
    user_agent="Chrome Test",
    ip_address="127.0.0.1",
)

print("Session Created")
print("Session ID:", session.id)
print("User ID:", session.user_id)

db.close()