from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

sit = {
    "category":
    "configs",
    "description":
    "",
    "infrastructure_capabilities": {},
    "infrastructure_targets": [
        {
            "environment": "development",
            "location": "test",
            "zone": "test"
        },
    ],
    "name":
    "test",
    "type":
    "stack_infrastructure_template"
}


def test_add_sit():
    response = client.post("stack_infrastructure_templates", json=sit)
    assert response.json() == sit
    assert response.status_code == 200


def test_get_sit():
    response = client.get("stack_infrastructure_templates/test")
    assert response.status_code == 200
    assert response.json() == sit


def test_get_sits():
    response = client.get("stack_infrastructure_templates")
    assert sit in response.json()
    assert response.status_code == 200
