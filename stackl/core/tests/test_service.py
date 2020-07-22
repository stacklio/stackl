from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

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

service_update = service.copy()
service_update['description'] = "Update description"


def test_add_service():
    response = client.post("services", json=service)
    assert response.status_code == 200
    assert response.json() == service


def test_get_service():
    response = client.get("services/vm_aws")
    assert response.status_code == 200
    assert response.json() == service


def test_get_services():
    response = client.get("services")
    assert response.status_code == 200
    assert response.json() == [service]


def test_update_service():
    response = client.put("services", json=service_update)
    assert response.status_code == 200
    assert response.json() == service_update


def test_delete_service():
    response = client.delete("services/vm_aws")
    assert response.status_code == 200
    response = client.get("services/vm_aws")
    assert response.status_code == 404


def test_get_service_expect_404():
    response = client.get("services/not_found")
    assert response.status_code == 404


def test_get_services_expect_none():
    response = client.get("services")
    assert response.status_code == 200
    assert response.json() == []
