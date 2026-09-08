from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_invalid_login():

    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "wrong"
        }
    )

    assert response.status_code == 401