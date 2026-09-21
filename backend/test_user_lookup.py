from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()

users = db.query(User).all()

print("Users found:", len(users))

for user in users:
    print(user.id, user.email)