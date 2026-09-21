from app.db.session import SessionLocal
from app.models.user import User
from app.services.session_service import SessionService

db = SessionLocal()
service = SessionService(db)

email = "akhil@example.com"

user = db.query(User).filter(User.email == email).first()

if not user:
    print("Register akhil@example.com first.")
else:
    session, token = service.create_session(
        user_id=user.id,
        user_agent="Chrome Test",
        ip_address="127.0.0.1",
    )

    print("Session Created")
    print("Session ID:", session.id)
    print("User ID:", session.user_id)
    print("Refresh Token:", token[:30], "...")