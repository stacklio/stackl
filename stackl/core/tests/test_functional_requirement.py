from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

functional_requirement = {
    'name': 'test',
    'category': 'configs',
    'type': 'functional_requirement',
    'params': {
        'test': 'test'
    },
    'secrets': {
        'test': 'test'
    },
    'description': 'test',
    'invocation': {
        'generic': {
            'description': 'test',
            'before_command': None,
            'tool': 'test',
            'image': 'test',
            'as_group': False
        },
        'aws': {
            'description': 'test',
            'before_command': None,
            'tool': 'test',
            'image': 'test',
            'as_group': False
        }
    },
    'outputs': {},
    'outputs_format': "json"
}

functional_requirement_update = functional_requirement.copy()
functional_requirement_update['secrets'] = {"update": "update"}
functional_requirement_update['params'] = {"update": "update"}
functional_requirement_update['invocation'] = {
    "generic": {
        "description": "update",
        "before_command": None,
        "image": "update",
        "tool": "update",
        "as_group": False
    },
    "aws": {
        "description": "update",
        "before_command": None,
        "image": "update",
        "tool": "update",
        "as_group": False
    }
}


def test_add_functional_requirement():
    response = client.post("functional_requirements",
                           json=functional_requirement)
    assert response.status_code == 200
    assert response.json() == functional_requirement


def test_get_functional_requirement():
    response = client.get("functional_requirements/test")
    assert response.status_code == 200
    assert response.json() == functional_requirement


def test_get_functional_requirements():
    response = client.get("functional_requirements")
    assert response.status_code == 200
    assert functional_requirement in response.json()


def test_update_functional_requirement():
    response = client.put("functional_requirements",
                          json=functional_requirement_update)
    assert response.status_code == 200
    assert response.json() == functional_requirement_update


def test_delete_functional_requirement():
    response = client.delete("functional_requirements/test")
    assert response.status_code == 200
    response = client.get("functional_requirements")
    assert response.status_code == 200
    assert functional_requirement not in response.json()
    assert functional_requirement_update not in response.json()


def test_get_functional_requirement_expect_404():
    response = client.get("functional_requirements/not_found")
    assert response.status_code == 404


def test_get_functional_requirement_expect_none():
    response = client.get("functional_requirements")
    assert response.status_code == 200
    assert response.json() == []
