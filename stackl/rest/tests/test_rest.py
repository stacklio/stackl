import socket

from fastapi.testclient import TestClient

from rest.main import app

client = TestClient(app)


def test_about():
    response = client.get('/about')
    assert response.status_code == 200
    assert response.json() == socket.gethostname()


def test_add_service():
    service = {
        "category": "items",
        "description": "Service to create a virtual machine on AWS",
        "functional_requirements": ["tf_vm_aws"],
        "name": "vm_aws",
        "params": {},
        "secrets": {},
        "resource_requirements": None,
        "type": "service"
    }
    response = client.post("/services", json=service)
    assert response.status_code == 200
    assert response.json() == service
