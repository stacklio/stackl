from fastapi.testclient import TestClient

from rest.main import app

client = TestClient(app)


def setup_module(module):
    service = {
        "category": "items",
        "description": "mock service",
        "functional_requirements": ["test_fr"],
        "name": "test_service",
        "params": {},
        "secrets": {},
        "resource_requirements": None,
        "type": "service"
    }
    client.post("/services", json=service)


def test_create_snapshot():
    response = client.post(f"/snapshots/service/test_service")
    assert response.status_code == 200
