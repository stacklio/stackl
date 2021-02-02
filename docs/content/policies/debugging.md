---
title: Debugging
kind: policies
weight: 3
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
## Debugging OPA

Following section describes how to debug OPA policies that Stackl uses.

### Requirements

- [OPA client](https://www.openpolicyagent.org/docs/latest/#running-opa)

### Evaluating a policy

To debug a OPA policy used by Stackl it is recommended to download the data passed to the policy and the policy itself. The data used can be found in the logs, look for `core.opa_broker` in the logs for OPA relevant logs. For example:

```log
2020-10-20 11:20:19.698 | DEBUG    |  .opa_broker:convert_sit_to_opa_data:126 - [OPABroker] convert_sit_to_opa_data. For sit_doc 'name='development' description='SIT updated at 2020-10-20 11h20m19s' infrastructure_targets=[InfrastructureTarget(environment='development', location='location', zone='k8s')] infrastructure_capabilities={'development.location.k8s': StackInfrastructureTarget(provisioning_parameters={'environment': 'development'}, cloud_provider='generic', secrets={}, resources={}, policies={}, agent='common', packages=['ct_k8s_nexus', 'ct_k8s_microservice', 'example-playbook'], tags={'environment': 'development'})} type='stack_infrastructure_template' category='configs''
2020-10-20 11:20:19.699 | DEBUG    | core.opa_broker.opa_broker:convert_sit_to_opa_data:144 - [OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{'infrastructure_targets': {'development.location.k8s': {'resources': {}, 'packages': ['ct_k8s_nexus', 'ct_k8s_microservice', 'example-playbook'], 'tags': {'environment': 'development'}, 'params': {'environment': 'development'}}}}'
2020-10-20 11:20:19.699 | DEBUG    | core.datastore.redis_store:get:21 - [RedisStore] get on key 'items/service/example-playbook'
2020-10-20 11:20:19.700 | DEBUG    | core.datastore.redis_store:get:31 - [RedisStore] StoreResponse for get: <StoreResponse. Status Code: 200. Reason: None. Content: {'name': 'example-playbook', 'category': 'items', 'type': 'service', 'params': {}, 'secrets': {}, 'description': 'example-playbook', 'functional_requirements': ['example-playbook'], 'resource_requirements': None}>
2020-10-20 11:20:19.700 | DEBUG    | core.opa_broker.opa_broker:convert_sat_to_opa_data:151 - [OPABroker] convert_sat_to_opa_data. For sat_doc 'name='example-playbook' description='example-playbook' services=['example-playbook'] policies={} category='configs' type='stack_application_template''
2020-10-20 11:20:19.700 | DEBUG    | core.datastore.redis_store:get:21 - [RedisStore] get on key 'configs/functional_requirement/example-playbook'
2020-10-20 11:20:19.701 | DEBUG    | core.datastore.redis_store:get:31 - [RedisStore] StoreResponse for get: <StoreResponse. Status Code: 200. Reason: None. Content: {'name': 'example-playbook', 'category': 'configs', 'type': 'functional_requirement', 'params': {'ansible_playbook_path': '/opt/ansible/playbook.yml'}, 'secrets': {}, 'description': 'example-playbook', 'invocation': {'generic': {'description': 'Example playbook', 'tool': 'ansible', 'image': 'stacklio/example-playbook:v1.0.0', 'before_command': None, 'as_group': False}}, 'outputs': {}, 'outputs_format': 'json'}>
2020-10-20 11:20:19.701 | DEBUG    | core.opa_broker.opa_broker:convert_sat_to_opa_data:171 - [OPABroker] convert_sat_to_opa_data. sat_as_opa_data '{'services': {'example-playbook': {'functional_requirements': {'example-playbook': {'generic': {'description': 'Example playbook', 'tool': 'ansible', 'image': 'stacklio/example-playbook:v1.0.0', 'before_command': None, 'as_group': False}}}, 'resource_requirements': None, 'params': {'ansible_playbook_path': '/opt/ansible/playbook.yml'}}}}'
2020-10-20 11:20:19.701 | DEBUG    | core.handler.stack_handler:evaluate_orchestration_policy:406 - [StackHandler] _handle_create. performing opa query with data: {'required_tags': {}, 'services': {'example-playbook': {'functional_requirements': {'example-playbook': {'generic': {'description': 'Example playbook', 'tool': 'ansible', 'image': 'stacklio/example-playbook:v1.0.0', 'before_command': None, 'as_group': False}}}, 'resource_requirements': None, 'params': {'ansible_playbook_path': '/opt/ansible/playbook.yml'}}}, 'infrastructure_targets': {'development.location.k8s': {'resources': {}, 'packages': ['ct_k8s_nexus', 'ct_k8s_microservice', 'example-playbook'], 'tags': {'environment': 'development'}, 'params': {'environment': 'development'}}}}
2020-10-20 11:20:19.702 | DEBUG    | core.opa_broker.opa_broker:ask_opa_policy_decision:33 - [OPABroker] ask_opa_policy_decision. For policy_package 'orchestration' and policy_rule 'solutions'' and data '{"required_tags": {}, "services": {"example-playbook": {"functional_requirements": {"example-playbook": {"generic": {"description": "Example playbook", "tool": "ansible", "image": "stacklio/example-playbook:v1.0.0", "before_command": null, "as_group": false}}}, "resource_requirements": null, "params": {"ansible_playbook_path": "/opt/ansible/playbook.yml"}}}, "infrastructure_targets": {"development.location.k8s": {"resources": {}, "packages": ["ct_k8s_nexus", "ct_k8s_microservice", "example-playbook"], "tags": {"environment": "development"}, "params": {"environment": "development"}}}}'
2020-10-20 11:20:19.710 | DEBUG    | core.opa_broker.opa_broker:ask_opa_policy_decision:51 - [OPABroker] ask_opa_policy_decision. response: {'result': {'fulfilled': True, 'services': {'example-playbook': ['development.location.k8s']}}}
2020-10-20 11:20:19.711 | DEBUG    | core.handler.stack_handler:evaluate_orchestration_policy:412 - [StackHandler] _handle_create. opa_result: {'fulfilled': True, 'services': {'example-playbook': ['development.location.k8s']}}
2020-10-20 11:20:19.711 | DEBUG    | core.opa_broker.opa_broker:ask_opa_policy_decision:33 - [OPABroker] ask_opa_policy_decision. For policy_package 'replicas' and policy_rule 'solutions'' and data '{"parameters": {"services": {"example-playbook": 2}}, "services": {"example-playbook": ["development.location.k8s"]}}'
2020-10-20 11:20:19.715 | DEBUG    | core.opa_broker.opa_broker:ask_opa_policy_decision:51 - [OPABroker] ask_opa_policy_decision. response: {'result': {'fulfilled': False, 'msg': 'Not enough targets for services {"example-playbook": ["development.location.k8s"]}'}}
2020-10-20 11:20:19.715 | DEBUG    | core.handler.stack_handler:evaluate_replica_policy:364 - [StackHandler] _handle_create. opa_result for replicas policy: {'fulfilled': False, 'msg': 'Not enough targets for services {"example-playbook": ["development.location.k8s"]}'}
```

In this example a user attempts to create two replicas of a SAT but only one target is available. We can copy the data from the logs to try and evaluate the replica policy ourselves. To do so, make sure to download the [OPA client](https://www.openpolicyagent.org/docs/latest/#running-opa).

First the orchestration policy is evaluated with the following data:

```json
{"required_tags": {}, "services": {"example-playbook": {"functional_requirements": {"example-playbook": {"generic": {"description": "Example playbook", "tool": "ansible", "image": "stacklio/example-playbook:v1.0.0", "before_command": null, "as_group": false}}}, "resource_requirements": null, "params": {"ansible_playbook_path": "/opt/ansible/playbook.yml"}}}, "infrastructure_targets": {"development.location.k8s": {"resources": {}, "packages": ["ct_k8s_nexus", "ct_k8s_microservice", "example-playbook"], "tags": {"environment": "development"}, "params": {"environment": "development"}}}}
```

As seen in the logs, the orchestration policy was completed successfully and returns a list of potential targets for the replica policy to use. Using the following data:

```json
{"parameters": {"services": {"example-playbook": 2}}, "services": {"example-playbook": ["development.location.k8s"]}}
```

Results in an error:

```log
2020-10-20 11:20:19.715 | DEBUG    | core.handler.stack_handler:evaluate_replica_policy:364 - [StackHandler] _handle_create. opa_result for replicas policy: {'fulfilled': False, 'msg': 'Not enough targets for services {"example-playbook": ["development.location.k8s"]}'}
```

To evaluate the given data with the replica policy manually, download the [replica policy](https://github.com/stacklio/stackl/blob/master/build/example_policies/policy_replicas.rego). Use the data from the logs and save it as a json file.

Once both files are available, run the following command to evaluate the policy:

```bash
opa eval -i input.json -d replica.rego 'data.replicas.solutions' -f pretty
```

This command results in the same error message. 

```log
opa eval -i input.json -d replica.rego 'data.replicas.solutions' -f pretty
{
  "fulfilled": false,
  "msg": "Not enough targets for services {\"example-playbook\": [\"development.location.k8s\"]}"
}
```

A solution would be to increase the targets manually or descrease the amount of replicas and verify if the policy is evaluated correctly. For example:

```json
{"parameters": {"services": {"example-playbook": 2}}, "services": {"example-playbook": ["development.location.k8s", "production.location.k8s"]}}
```

Results in:

```log
opa eval -i input.json -d replica.rego 'data.replicas.solutions' -f pretty
{
  "fulfilled": true,
  "services": {
    "example-playbook": [
      "development.location.k8s",
      "production.location.k8s"
    ]
  }
}
```

This method can be used to debug any policy in OPA used by Stackl.

## References

- [OPA documentation](https://www.openpolicyagent.org/docs/latest/)
- [OPA eval](https://www.openpolicyagent.org/docs/latest/#2-try-opa-eval)
- [OPA client](https://www.openpolicyagent.org/docs/latest/#running-opa)
