from uuid import uuid4

from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository


def test_create_and_get_user():
    db = SessionLocal()
    repository = UserRepository(db)

    email = f"{uuid4()}@example.com"

    user = User(
        full_name="Repository Test",
        email=email,
        password_hash="hashed_password"
    )

    repository.create(user)

    fetched = repository.get_by_email(email)

    assert fetched is not None
    assert fetched.email == email
    assert fetched.full_name == "Repository Test"

    db.delete(fetched)
    db.commit()
    db.close()


def test_get_all_users():
    db = SessionLocal()
    repository = UserRepository(db)

    users = repository.get_all()

    assert isinstance(users, list)

    db.close()