from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

environment = {
    "category": "configs",
    "description": "development environment",
    "name": "development",
    "params": {
        "test": "test",
    },
    "resources": {},
    "policies": {},
    "packages": [
        "test",
    ],
    "outputs": {},
    "cloud_provider": "aws",
    "tags": {
        "environment": "development"
    },
    "secrets": {
        "vsphere_credentials": "secret/data/infra/vmw"
    },
    "type": "environment",
    "agent": "development"
}

location = {
    'name': 'belgium',
    'category': 'configs',
    'type': 'location',
    'cloud_provider': '',
    'params': {
        'test': 'test'
    },
    'secrets': {
        'test': 'test'
    },
    'outputs': {},
    'resources': {},
    'policies': {},
    'packages': [],
    'tags': {},
    'agent': '',
    'description': 'Belgium DC'
}

environment_update = environment.copy()
environment_update['description'] = "Update description"
environment_update['packages'] = ['update']
environment_update['secrets'] = {}
environment_update['tags'] = {'environment': 'prod'}
environment_update['params'] = {'update': 'update'}


def test_prepare_snapshot():
    response = client.post("infrastructure_base", json=environment)
    assert response.status_code == 200
    assert response.json() == environment
    response = client.post("infrastructure_base", json=location)
    assert response.status_code == 200
    assert response.json() == location


def test_add_snapshot():
    response = client.post("snapshots/environment/development")
    assert response.status_code == 200
    response = client.get("snapshots/environment/development")
    assert response.status_code == 200
    response = client.post("snapshots/location/belgium")
    assert response.status_code == 200
    response = client.get("snapshots/location/belgium")
    assert response.status_code == 200


def test_get_snapshots():
    response = client.get("snapshots/environment/development")
    for snapshot in response.json():
        assert snapshot['snapshot']['name'] == "development"
        assert snapshot['snapshot']['type'] == "environment"


def test_restore_latest_environment():
    response = client.put("infrastructure_base", json=environment_update)
    assert response.status_code == 200
    assert response.json() == environment_update
    response = client.post("snapshots/restore/environment/development")
    assert response.status_code == 200
    response = client.get("infrastructure_base/environment/development")
    assert response.status_code == 200
    assert response.json() == environment


def test_restore_specific_environment():
    response = client.put("infrastructure_base", json=environment_update)
    assert response.status_code == 200
    assert response.json() == environment_update
    response = client.get("snapshots/environment/development")
    assert response.status_code == 200
    snapshots = response.json()
    response = client.post(f"snapshots/restore/{snapshots[-1]['name']}")
    assert response.status_code == 200
    response = client.get("infrastructure_base/environment/development")
    assert response.status_code == 200
    assert response.json() == environment


def test_delete_snapshot():
    response = client.get("snapshots/environment/development")
    assert response.status_code == 200
    snapshots = response.json()
    snapshot_name = snapshots[-1]['name']
    response = client.delete(f"snapshots/{snapshot_name}")
    assert response.status_code == 200
    response = client.get("snapshots/environment/development")
    for snapshot in response.json():
        assert snapshot['name'] != snapshot_name
    response = client.get("snapshots/location/belgium")
    assert response.status_code == 200
    snapshots = response.json()
    snapshot_name = snapshots[-1]['name']
    response = client.delete(f"snapshots/{snapshot_name}")
    assert response.status_code == 200
    response = client.get("snapshots/location/belgium")
    for snapshot in response.json():
        assert snapshot['name'] != snapshot_name


def test_get_snapshot_expect_404():
    response = client.get("snapshots/not_found")
    assert response.status_code == 404


def test_get_snapshot_expect_none():
    response = client.get("snapshots/environment/development")
    assert response.status_code == 200
    assert response.json() == []
    response = client.get("snapshots/location/belgium")
    assert response.status_code == 200
    assert response.json() == []
