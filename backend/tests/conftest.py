from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_current_user
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture(autouse=True)
def disable_auto_embeddings(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "EMBEDDING_AUTO_GENERATE", False)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = testing_session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def user_factory(db_session: Session):
    def create_user(
        *,
        email: str | None = None,
        full_name: str = "Test User",
        password: str | None = None,
        is_active: bool = True,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email or f"{uuid4()}@example.com",
            password_hash=hash_password(password) if password else "not-used",
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def authenticated_user(client: TestClient):
    def register_and_login(
        *,
        email: str | None = None,
        full_name: str = "Integration User",
        password: str = "Password123",
    ) -> dict:
        credentials = {
            "full_name": full_name,
            "email": email or f"{uuid4()}@example.com",
            "password": password,
        }
        registration = client.post("/auth/register", json=credentials)
        assert registration.status_code == 200, registration.text

        login = client.post(
            "/auth/login",
            json={
                "email": credentials["email"],
                "password": credentials["password"],
            },
        )
        assert login.status_code == 200, login.text

        tokens = login.json()
        return {
            "user": registration.json(),
            "credentials": credentials,
            "tokens": tokens,
            "headers": {
                "Authorization": f"Bearer {tokens['access_token']}"
            },
        }

    return register_and_login
