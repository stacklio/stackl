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

environment_update = environment.copy()
environment_update['description'] = "Update description"
environment_update['packages'] = ['update']
environment_update['secrets'] = {}
environment_update['tags'] = {'environment': 'prod'}
environment_update['params'] = {'update': 'update'}


def test_add_environment():
    response = client.post("infrastructure_base", json=environment)
    assert response.status_code == 200
    assert response.json() == environment


def test_get_environment():
    response = client.get("infrastructure_base/environment/development")
    assert response.status_code == 200
    assert response.json() == environment


def test_get_environments():
    response = client.get("infrastructure_base/environment")
    assert response.status_code == 200
    assert response.json() == [environment]


def test_update_environment():
    response = client.put("infrastructure_base", json=environment_update)
    assert response.status_code == 200
    assert response.json() == environment_update


def test_delete_environment():
    response = client.delete("infrastructure_base/environment/development")
    assert response.status_code == 200
    response = client.get("infrastructure_base/environment/development")
    assert response.status_code == 404


def test_get_environment_expect_404():
    response = client.get("infrastructure_base/environment/development")
    assert response.status_code == 404


def test_get_environments_expect_none():
    response = client.get("infrastructure_base/environment")
    assert response.status_code == 200
    assert response.json() == []


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

location_update = location.copy()
location_update['description'] = "France DC"
location_update['params'] = {"update": "update"}
location_update['secrets'] = {"update": "update"}


def test_add_location():
    response = client.post("infrastructure_base", json=location)
    assert response.status_code == 200
    assert response.json() == location


def test_get_location():
    response = client.get("infrastructure_base/location/belgium")
    assert response.status_code == 200
    assert response.json() == location


def test_get_locations():
    response = client.get("infrastructure_base/location")
    assert response.status_code == 200
    assert response.json() == [location]


def test_update_location():
    response = client.put("infrastructure_base", json=location_update)
    assert response.status_code == 200
    assert response.json() == location_update


def test_delete_location():
    response = client.delete("infrastructure_base/location/belgium")
    assert response.status_code == 200
    response = client.get("infrastructure_base/location/belgium")
    assert response.status_code == 404


def test_get_location_expect_404():
    response = client.get("infrastructure_base/location/belgium")
    assert response.status_code == 404


def test_get_locations_expect_none():
    response = client.get("infrastructure_base/location")
    assert response.status_code == 200
    assert response.json() == []


zone = {
    'name': 'test_zone',
    'category': 'configs',
    'type': 'zone',
    'cloud_provider': '',
    'params': {
        'test': 'test'
    },
    'secrets': {},
    'outputs': {},
    'resources': {},
    'policies': {},
    'packages': [],
    'tags': {},
    'agent': '',
    'description': 'Dome AWS zone'
}

zone_update = zone.copy()
zone_update['params'] = {"update": "update"}
zone_update['secrets'] = {"update": "update"}
zone_update['description'] = "Update description"


def test_add_zone():
    response = client.post("infrastructure_base", json=zone)
    assert response.status_code == 200
    assert response.json() == zone


def test_get_zone():
    response = client.get("infrastructure_base/zone/test_zone")
    assert response.status_code == 200
    assert response.json() == zone


def test_get_zones():
    response = client.get("infrastructure_base/zone")
    assert response.status_code == 200
    assert response.json() == [zone]


def test_update_zone():
    response = client.put("infrastructure_base", json=zone_update)
    assert response.status_code == 200
    assert response.json() == zone_update


def test_delete_zone():
    response = client.delete("infrastructure_base/zone/test_zone")
    assert response.status_code == 200
    response = client.get("infrastructure_base/zone/test_zone")
    assert response.status_code == 404


def test_get_zone_expect_404():
    response = client.get("infrastructure_base/zone/test_zone")
    assert response.status_code == 404


def test_get_zones_expect_none():
    response = client.get("infrastructure_base/zone")
    assert response.status_code == 200
    assert response.json() == []
