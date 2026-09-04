from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository

db = SessionLocal()

repository = UserRepository(db)

user = User(
    full_name="Akhil Reddy",
    email="akhil@example.com",
    password_hash="temporary_hash"
)

existing = repository.get_by_email(user.email)

if existing:
    print("User already exists.")
else:
    created = repository.create(user)
    print("Created User:", created.id)

fetched = repository.get_by_email("akhil@example.com")
print("Fetched:", fetched.full_name)

db.close()