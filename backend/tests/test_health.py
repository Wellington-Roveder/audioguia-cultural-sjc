from app.main import app
from fastapi.testclient import TestClient

cliente = TestClient(app)


def test_health_check():
    response = cliente.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
