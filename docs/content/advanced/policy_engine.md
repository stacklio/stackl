---
title: Policy Engine
kind: advanced
weight: 5
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

STACKL uses an open source, general-purpose policy engine, called Open Policy Agent (OPA), to offload policy enforcement and decision making for applications, infrastructure, and authorization and authentication.
OPA, available from [https://www.openpolicyagent.org/](https://www.openpolicyagent.org/), is a powerful and flexible open-source tool that uses a high-level declarative language to specify policy as code and offers a simple APIs to offload policy decision-making.
OPA is commonly used to enforce policies for microservices, Kubernetes, CI/CD pipelines, API gateways, and more.
STACKL integrates OPA to offload queries for decision making based on the user's IT environment and input, which may be certain policies, application placement, authorization, and so on.

STACKL uses the policy engine for three specific purposes:

1. To create orchestration solutions for applications as stack instances by matching the requirements of a SAT to the requirements and capabilities of a SIT and considering orchestration policies
2. (TODO) Work-in-progress. To manage the infrastructure, for instance, autonomously updating infrastructure capabilities
3. (TODO) Work-in-progress. To manage user authentication and authorization

In general, policy engines work through an input file that models a system and reasons over them through policies to provide results that can be used for decision making and policy enforcement.
OPA uses a high-level declarative language, Rego, to create policies which consist out of rules that govern how the system should behave.
Entities can then provide data to OPA and query it for policy decisions.
How OPA as a policy engine is integrated in STACKL to achieve the above purposes is described in the following sections.

# Stack orchestration

STACKL works through modelling the IT environment through SITs, including infrastructure capabilities and additional requirements (i.e., policies) and describing applications through SATs, which specify services and their functional, resource and policy requirements.
Accordingly, this is a natural match to what a policy engine needs: rules (i.e., policies) and data to reason over.

Thus, STACKL uses OPA for stack orchestration through:

- Providing OPA with default policies that model standard requirements for any SIT and SAT placement solution
- Extracting additional policies from the SIT and SAT and providing these to OPA as well
- Extracting the modeling and description data of the SIT and SAT
- Querying OPA for placement solutions for the data with all the policies
- Storing the resulting policy decision as a set of placement solutions in a ST

The following sections describe in detail how STACKL uses policies and how they are managed with respect to OPA to obtain placement solutions

## Default policies

Default policies for stack orchestration are basic constraints any workload placement solution must adhere to.
These are general rules that check for each potential infrastructure target three basic requirements for each service and the application as a whole:

1. Do the target resource capabilities satisfy the service's resource requirements?
2. Do the target package capabilities satisfy the service's functional requirements?
3. Does the target have the required tags for the application?

## SAT policy template

SAT policy templates are in the following format:

```yaml
category: configs
description: hasparams policy
name: hasparams
type: policy_template
inputs: [params]
policy: |
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
```

In this example the policy uses params as input. If possible targets are found they are returned in the `targets` field and `fulfilled` is set to `true`. If no possible targets are found, `fulfilled` is `false` and a message describing the reason are returned.

To use this policy in a SAT, add it like this:

```yaml
category: configs
description: ''
name: sat_example
policies:
  hasparams:
    - params: ["dns_servers"]
      service: service_example
    - params: ["dns_servers"]
      service: service_example2
services:
- service_example
type: stack_application_template
```

Each of these policies will determine which infrastructure targets are suitable for the service.

## Replica policy

After all the SAT policies are evaluated, the replica policy will choose on how many targets the service will be deployed. Replicas can be added when creating a stack instance:

```bash
stackl create instance --stack-application-template <sat-example> --stack-infrastructure-template <sit-example> --replicas '{"service-name": 2}' <instance-name>
```

OPA evaluates if enough targets are available after evaluating all other policies first.

## SIT policy template

A SIT policy is a policy that defines extra constraints before applying a stack instance to an infrastructure target.

An example of a SIT policy:

```yaml
category: configs
description: allowedrepositories policy
name: allowedrepositories
type: policy_template
inputs: [repositories]
policy: |
  package allowedrepositories
  infringement[{"msg": msg}] {
    invocation := input.services[_].functional_requirements[fr]
    satisfied := [good |
      repo = input.parameters.repositories[_]
      good = startswith(invocation.image, repo)
    ]
    not any(satisfied)
    msg := sprintf("functional_requirement {%v} has an invalid image repository {%v}, must be one of {%v}", [fr, invocation.image, input.parameters.repositories])
  }
```

This policy forces a target to only use invocation images from allowed repositories.

SIT policies can be used within infrastructure documents (location, zone and enivornment).

An example of an environment using this policy:

```yaml
category: configs
description: development environment
name: development
params:
  foo: bar
resources: {}
packages:
  - example-fr
tags:
  environment: development
type: environment
policies:
  allowedrepositories:
    repositories: ["repo.example.com", "repo2.example.com"]
```

## Create a policy template

The policy name and package name must be the same for a policy.

 There are a few rules for the Rego constraint source code:

   1. Everything is contained in one package
   1. Limited external data access
      - No imports
   1. Specific rule signature schema (described below)

### Signature

While template authors are free to include whatever rules and functions they wish
to support their constraint, the main entry point called by the framework has a
specific signature.

#### SAT policy

```rego
solutions = {"fulfilled": true, "targets": targets} {
  # rule body
} else = {"fulfilled": false, "msg": msg} {
  msg := "Reason for failure"
}
```

`targets` is a list of infrastructure targets where the specific service can be deployed.

Example input:

```json
{
  "parameters": {
    "params": [
      "foo"
    ]
  },
  "services": {
    "postgres": {
      "functional_requirements": {
        "postgres": {
          "image": "repo.example.com/postgres:latest",
          "tool": "terraform"
        }
      },
      "resource_requirements": {},
      "params": {
        "foo": "bar"
      }
    }
  },
  "infrastructure_targets": {
    "vsphere.brussels.vmw-vcenter-01": {
      "resources": {},
      "packages": [
        "postgres"
      ],
      "tags": {
        "environment": "dev"
      },
      "params": {
        "foo": "bar"
      }
    }
  }
}
```

This example checks if a SAT has a certain parameter.

Example output if the service could be deployed on `vsphere.brussels.vmw-vcenter-01`:

```json
{
  "fulfilled": true,
  "targets": [
    "vsphere.brussels.vmw-vcenter-01"
  ]
}
```

Example output if the service could not be deployed:

```json
{
  "fulfilled": false,
  "msg": "No target has all the required params"
}
```

#### SIT policy

```rego
infringement[{"msg": msg}] {
  # return message if policy failed
}
```

Example output for a SIT policy that failed:

```json
[
  {
    "msg": "functional_requirement {postgres} has an invalid image repository {repository.example.com}, must be one of {[\"repo.example.com\"]}"
  }
]
```

If the policy succeeds no message is returned.

# Infrastructure management

# User authentication and authorization