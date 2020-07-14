from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

sat = {
    "category": "configs",
    "description": "",
    "name": "test",
    "policies": {
        "hostpolicy": [{
            "host": "windows-hosts",
            "service": "vm_vmw"
        }]
    },
    "services": ["test"],
    "type": "stack_application_template"
}

sat_update = sat.copy()
sat_update['description'] = "update"
sat_update['services'] = ["update"]
sat_update['policies'] = {"test": [{"update": "update", "service": "vm_vmw"}]}


def test_create_sat():
    response = client.post("stack_application_templates", json=sat)
    assert response.status_code == 200
    assert response.json() == sat


def test_get_sat():
    response = client.get("stack_application_templates/test")
    assert response.status_code == 200
    assert response.json() == sat


def test_get_sats():
    response = client.get("stack_application_templates")
    assert response.status_code == 200
    assert sat in response.json()


def test_get_sat_expect_404():
    response = client.get("stack_application_templates/not-found")
    assert response.status_code == 404


def test_update_sat():
    response = client.put("stack_application_templates", json=sat_update)
    assert response.status_code == 200
    assert response.json() == sat_update


def test_delete_sat():
    response = client.delete("stack_application_templates/test")
    assert response.status_code == 200
    response = client.get("stack_application_templates/test")
    assert response.status_code == 404
    response = client.get("stack_application_templates")
    assert sat not in response.json()
    assert sat_update not in response.json()
