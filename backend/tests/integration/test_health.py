from fastapi.testclient import TestClient


def test_root_and_health_endpoints(client: TestClient):
    root = client.get("/")
    health = client.get("/health/")

    assert root.status_code == 200
    assert root.json()["message"] == "AI Workspace V2 Backend Running"
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
