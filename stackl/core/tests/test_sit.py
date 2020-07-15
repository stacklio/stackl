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

sit_update = sit.copy()
sit_update['infrastructure_targets'] = [
    {
        "environment": "update",
        "location": "update",
        "zone": "update"
    },
]
sit_update['description'] = "update"


def test_get_sits_expect_none():
    response = client.get("stack_infrastructure_templates")
    assert [] == response.json()
    assert response.status_code == 200


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


def test_update_sit():
    response = client.put("stack_infrastructure_templates", json=sit_update)
    assert response.status_code == 200
    assert response.json() == sit_update


def test_delete_sit():
    response = client.delete(f"stack_infrastructure_templates/{sit['name']}")
    assert response.status_code == 200
    response = client.get(f"stack_infrastructure_templates/{sit['name']}")
    assert response.status_code == 404


def test_get_sit_expect_404():
    response = client.get("stack_infrastructure_templates/not-found")
    assert response.status_code == 404
