from fastapi.testclient import TestClient

from core.main import app

client = TestClient(app)

policy = """
  package hasparams
  solutions = {"fulfilled": true, "targets": targets} {
    params := input.parameters.params
    targets := [it |
      infra_target_params := input.infrastructure_targets[it].params
      params_set := {x | x := params[_]}
      infra_target_keys := {x | infra_target_params[x] }
      union :=  params_set & infra_target_keys
      count(union) >= count(params)
    ]
    count(targets) > 0
  } else =  {"fulfilled": false, "msg": msg} {
    msg := "No target has all the required params"
  }
"""

policy_template = {
    "category": "configs",
    "description": "hasparams policy",
    "name": "hasparams",
    "type": "policy_template",
    "inputs": ["params"],
    "outputs": None,
    "policy": policy
}

policy_template_update = policy_template.copy()
policy_template_update['description'] = "update"
policy_template_update['policy'] = "update"

# def test_get_policy_templates_expect_none():
#     response = client.get("policy_templates")
#     assert response.status_code == 200
#     assert response.json() == []


def test_add_policy_template():
    response = client.put("policy_templates", json=policy_template)
    print(response.json())
    print(policy_template)
    assert response.status_code == 200
    assert response.json() == policy_template


def test_get_policy_template():
    response = client.get("policy_templates/hasparams")
    assert response.status_code == 200
    assert response.json() == policy_template


def test_update_policy_template():
    response = client.put("policy_templates", json=policy_template_update)
    assert response.status_code == 200
    assert response.json() == policy_template_update


def test_get_policy_templates():
    response = client.get("policy_templates")
    assert response.status_code == 200
    assert response.json() == [policy_template_update]


def test_get_policy_template_expect_404():
    response = client.get("policy_templates/not-found")
    assert response.status_code == 404
