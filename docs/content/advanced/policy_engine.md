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

## SIT and SAT policies

To maintain a general solution, independent from OPA, and keep infrastructure and application modelling as pure K/V documents, SITs and SATs use policy template documents.
Each SIT and SAT can specify in a K/V pair the name of the policy template and the value of its parameters.
The policy template itself is a config K/V document that describes its inputs (parameters) and includes the policy code as a string.
This policy can be present as well in its native language (in OPA's case, Rego) for reference and explicit testing.

The policy name thus refers to the config document.
Parameters are specific to the policy used.
There are two types of parameters: **target parameters**, the services and targets the the policy applies to and are mandatory, and **value parameters**, parameters that allow to fine-tune the policy.
To use the policy as configured in the SIT or SAT, STACKL retrieves it from its database, reads in the string and fills in the values.

A simple example for a SAT and a policy is given here:

```json
{ #sat_example.json
    "name": "web",
    "type": "stack_application_template",
    "category": "configs",
    "services": [
        "webserver",
        "database"
    ],
    "policies": {
        "replicas" : ["webserver", 2]
    }
}

{ #policy_template_replicas.json
    "name": "replicas",
    "description": "Policy to ensure the service has at least the given amount of replicas",
    "category" : "configs",
    "type": "policy",
    "policy": "\nreplicas = x {\n\tservice = input.policy_input.service\n\tamount = input.policy_input.amount\n\tcount(input.services[service]) >= amount\n\tx = {service: array.slice(input.services[service], 0, amount)}\n} else = x {\n    x = {input.policy_input.service: []}\n}\n",
    "inputs": ["service","amount"]
}
```

## Querying OPA for stack orchestration

STACKL queries OPA for a stack orchestration result through iterative policy evaluation, either directly in a single generated policy file that contains all rules consecutively or through querying for policy decisions for each policy successively.
In both cases, the process proceeds roughly the same: first, an initial set of service to targets map is made, second, the special replica policy is applied in case a service needs to be replicated, expanding the solution set, and finally, any additional policies are applied and a final set of placement solutions is returned.

To illustrate with an example that includes the replication of a serivice, the first initial result for a given SIT with three targets and a SAT with two services might be:

```json
{
  "initial_service_to_targets_map": {
    "windows_2019_vmw_vsphere": [
      "vsphere.brussels.vmw-vcenter-01",
      "vsphere.houston.vmw-vcenter-03",
      "vsphere.shanghai.vmw-vcenter-02"
    ],
    "windows_2019_vmw_vsphere_heavy": [
      "vsphere.brussels.vmw-vcenter-01"
    ]
  }
}
```

This map only tells which targets could potentially host the basic requirements of a service.
Now, this map is processed to a real solution where each service has a single target.
Here, the special replica policy is applied first, if specified, so that services can be replicated and resulting in, for instance, :

```json
{
    "basic_application_placement_solution_sets": [
    {
        "windows_2019_vmw_vsphere_1": "vsphere.brussels.vmw-vcenter-01",
        "windows_2019_vmw_vsphere_2": "vsphere.brussels.vmw-vcenter-01",
        "windows_2019_vmw_vsphere_heavy": "vsphere.brussels.vmw-vcenter-01"
    },
    {
        "windows_2019_vmw_vsphere_1": "vsphere.brussels.vmw-vcenter-01",
        "windows_2019_vmw_vsphere_2": "vsphere.brussels.vmw-vcenter-02",
        "windows_2019_vmw_vsphere_heavy": "vsphere.brussels.vmw-vcenter-01"
    },
    {
        "windows_2019_vmw_vsphere_1": "vsphere.brussels.vmw-vcenter-02",
        "windows_2019_vmw_vsphere_2": "vsphere.brussels.vmw-vcenter-02",
        "windows_2019_vmw_vsphere_heavy": "vsphere.brussels.vmw-vcenter-01"
    },
...(and so on)
]
}
```

This is a set of basic solutions for stack orchestration without considering any additional policies (excepting the replica policy).
This set then is filtered further, where, for instance, a policy for unique service hosting would discard the first and third solution set above (as the replicated service share a host there).
The end result is a set of solutions where each solution contains a mapping of a service to a target and the mapping satisfies the requirements of both the initial SIT and SAT.
This result is then stored in a ST and can be initiated to become a SI by selecting one of these solutions, thus completing the stack orchestration process.

# Infrastructure management

# User authentication and authorization