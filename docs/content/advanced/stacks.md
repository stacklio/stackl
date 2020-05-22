---
title: Stacks
kind: advanced
weight: 3
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

A Stack is a declarative description of an application and the IT infrastructure it may run on.
A Stack is instantiated as a **Stack Instance (SI)** which comes from a **Stack Template (ST)** which itself is the result of  a **Stack Application Template (SAT)** and a **Stack Infrastructure Template (SIT)**.
STACKL creates a ST by constraint solving the requirements of the SAT and the capabilities of the SIT to a deployment mapping of the described application to the modelled IT infrastructure at that point in time.
The result is a set of possible placement solutions, if any.
An instantiation of a solution of the ST on the infrastructure is called a Stack Instance (SI).
Stacks are thus a conceptual element that describes the desired orchestration of an application in the IT environment.
SATs, SITs, STs and SIs are stored documents which are given, processed, tracked, and maintained in the datastore and represent the parts and stages of a Stack.

Users separately specify their infrastructure, modelling in a SIT what is available and how, from their applications, described as a collection of services in a microservice architecture.
Separate specification decouples applications from the infrastructure, allowing different SATs to be matched to different SITs, promoting flexibility, adaptability, and re-use.
Operators can submit a Stack to STACKL as a combination of a SAT and SIT.
If the stack is instantiable, STACKL returns the set of possible instantiations in a ST which can become a SI, or the actual running application.

## Stack Application Template

A SAT describes the application as a collection of services (software entities) that have functional and resource requirements (FR and RR) and policies which describes extra-functional requirements such as replication.
The SAT contains the services with their FRs and RRs and specifies additional policies to determine application behavior and runtime.
The resulting set of these requirements and policies are the constraints of the application to be able to run as desired on a given infrastructure.

Services are either stored in separate documents or specified in the SAT itself.
FRs are what the service is supposed to do and with what or how.
These map to configuration packages for the software host so that it can perform certain functions, such as supporting a Linux environment or a network configuration.
(TODO) FRs can inherit from other FRs.
K/V pairs of an FR override those of the preceding FR.
FRs are stored in separate documents.
FRs can specify RRs that help determine the minimum RRs of the service which itself can specify RRs.
FRs also state the invocation process that is needed to instantiate the FR.

RRs are what resources the service needs to functions
These map the resource requirements of the hosting infrastructure.
These are the minimum set of the requirements of the FRs, if specified, and the specified ones by the service.

Policies are additional specifications for how the service or applications functions.
These map to behavioral constraints on and across services, such as high availability of a service through redundancy or a low latency requirement between two services.
They can be both derived from the set of FRs or explicitly specified for the application.

A default policy that is always present is that the RR of the SAT can be satisfied.

### Example: Simple SAT

```json
 #stack_application_template_example_simple_web.json
{
    "name": "example_simple_web",
    "description": "An example simple web application consisting of a webserver and a database",
    "type": "stack_application_template",
    "category": "configs",
    "services": [
        "example_webserver",
        "example_database"
    ],
    "policies": {}
}
```

```json
#service_example_web.json
{
    "name": "example_web",
    "type": "service",
    "category": "items",
    "functional_requirements": ["linux","flask"],
    "resource_requirements": {
        "cpu_cores": "2",
        "memory": "2GB",
        "disk":"1GB"
    }
}
#service_example_database.json
{
    "name": "example_database",
    "type": "service",
    "category": "items",
    "functional_requirements": ["redis"],
    "resource_requirements": {
        "cpu_cores": "1",
        "memory": "2GB",
        "disk": "20GB"
    }
}
```

```json
#functional_requirement_linux.json
{
    "category": "configs",
    "description": "type functional_requirement with name example linux",
    "invocation": {
        "description": "Deploys a Linux VM",
        "image": "TODO",
        "tool": "TODO"
    },
    "name": "example_linux",
    "params": {},
    "type": "functional_requirement"
}
#functional_requirement_flask.json
{
    "category": "configs",
    "description": "type functional_requirement with name example flask",
    "invocation": {
        "description": "Deploys a flask webserver",
        "image": "TODO",
        "tool": "TODO"
    },
    "name": "example_flask",
    "params": {},
    "type": "functional_requirement"
}
#functional_requirement_redis.json
{
    "category": "configs",
    "description": "type functional_requirement with name example redis",
    "invocation": {
        "description": "Deploys a redis database",
        "image": "TODO",
        "tool": "TODO"
    },
    "name": "example_redis",
    "params": {},
    "type": "functional_requirement"
}
```

### Example: SAT with additional policies

```json
#stack_application_template_example_complex_web.json
{
    "name": "example_complex_web",
    "description": "An example complex web application consisting of a webserver that should be replicated for redundancy in a different zone and a database which should be on the same target as the primary webserver",
    "type": "stack_application_template",
    "category": "configs",
    "services": [
        "example_web",
        "example_database"
    ],
    "policies": {
        "replicas": ["example_web", 2],
        "same_location": [["example_web_1", "example_database"]],
        "separate_target":[["example_web_1", "example_web_2"]]
    }
}
```

```json
#policy_template_replicas.json
{
    "name": "replicas",
    "description": "PolicyTemplate to ensure the service has at least the given amount of replicas",
    "category": "configs",
    "type": "policy",
    "policy": "\nreplicas = x {\n\tservice = input.policy_input.service\n\tamount = input.policy_input.amount\n\tcount(input.services[service]) >= amount\n\tx = {service: array.slice(input.services[service], 0, amount)}\n} else = x {\n   x = {input.policy_input.service: []}\n}",
    "inputs": [
        "service",
        "amount"
    ]
}
#policy_template_same_location.json
{
    "name": "same_location",
    "description": "PolicyTemplate to ensure the given services are at the same location",
    "category": "configs",
    "type": "policy",
    "policy": "same_location(application_placement_solutions){\n\tsome i, j\n\tservice1 = input.policy_input.services[i]\n\tservice2 = input.policy_input.services[j]\n\tsolution = application_placement_solutions[_]\n\tlocation_service1 = split(solution[service1],\".\")[1]\n\tlocation_service2 = split(solution[service2],\".\")[1]\n\tlocation_service1 == location_service2\n}",
    "inputs": [
        "services"
    ]
}
#policy_template_separate_target.json
{
    "name": "separate_target",
    "description": "PolicyTemplate to ensure the given services are on separate targets",
    "category": "configs",
    "type": "policy",
    "policy": "separate_target(application_placement_solutions){\n\tsome i, j\n\tservice1 = input.policy_input.services[i]\n\tservice2 = input.policy_input.services[j]\n\tsolution = application_placement_solutions[_]\n\tsolution[service1] == solution[service2]\n}",
    "inputs": [
        "services"
    ]
}
```

## Stack Infrastructure Template

A SIT models the available infrastructure.
It describes the infrastructure in terms of the environment, location, and zones and explicitly specifies their relationship in a set of infrastructure targets.
Environment, location, and zones are separate documents which provide the data needed to access them as well as infrastructure-specific policies.
An infrastructure target is the result of merging these documents where the K/V pairs of the zone override the location which override the environment.
Each infrastructure target has capabilities.
These can vary over time due to dynamic factors (e.g., load on a server, power outages, ...).
(TODO) As such, each SIT has an update policy which specifies when the capabilities of the infrastructure targets should be determined.

### Example: Simple Stack Infrastructure Template

```json
# stack_infrastructure_template_simple_complex_web_host.json
{
    "category": "configs",
    "description": "An example SIT that can support the example simple web SAT",
    "infrastructure_capabilities": {
        "production.example_brussel.example_cluster1": {
            "resources": {
                "cpu_cores": "20",
                "memory": "20GB",
                "disk": "1000GB"
            },
            "packages": [
                "redis",
                "linux",
                "flask"
            ],
            "cluster": "TODO",
            "datacenter": "TODO",
            "datastore": "TODO",
            "hostname": "TODO",
            "network": "TODO",
            "password": "TODO",
            "username": "TODO"
        }
    },
    "infrastructure_targets": [
        {
            "environment": "production",
            "location": "example_brussel",
            "zone": "example_cluster1"
        }
    ],
    "name": "example_simple_web_host",
    "type": "stack_infrastructure_template"
}
```

### Example: Complex Stack Infrastructure Template

```json
# stack_infrastructure_template_example_complex_web_host.json
{
    "category": "configs",
    "description": "An example SIT that can support the example complex web SAT",
    "infrastructure_capabilities": {
        "production.example_brussel.example_cluster1": {
            "resources": {
                "cpu_cores": "20",
                "memory": "20GB",
                "disk": "1000GB"
            },
            "packages": [
                "redis",
                "linux",
                "flask"
            ],
            "cluster": "TODO",
            "datacenter": "TODO",
            "datastore": "TODO",
            "hostname": "TODO",
            "network": "TODO",
            "password": "TODO",
            "username": "TODO"
        },
        "production.example_brussel.example_cluster2": {
            "resources": {
                "cpu_cores": "20",
                "memory": "20GB",
                "disk": "1000GB"
            },
            "packages": [
                "redis",
                "linux",
                "flask"
            ],
            "cluster": "TODO",
            "datacenter": "TODO",
            "datastore": "TODO",
            "hostname": "TODO",
            "network": "TODO",
            "password": "TODO!",
            "username": "TODO"
        },
        "production.example_paris.example_cluster1": {
            "resources": {
                "cpu_cores": "20",
                "memory": "20GB",
                "disk": "1000GB"
            },
            "packages": [
                "redis",
                "linux",
                "flask"
            ],
            "cluster": "TODO",
            "datacenter": "TODO",
            "datastore": "TODO",
            "hostname": "TODO",
            "network": "TODO",
            "password": "TODO!",
            "username": "TODO"
        }
    },
    "infrastructure_targets": [
        {
            "environment": "production",
            "location": "example_brussel",
            "zone": "example_cluster1"
        },
        {
            "environment": "production",
            "location": "example_brussel",
            "zone": "example_cluster2"
        },
        {
            "environment": "production",
            "location": "example_paris",
            "zone": "example_cluster1"
        }
    ],
    "name": "example_complex_web_host",
    "type": "stack_infrastructure_template"
}
```

## Stack Template and Instance

A ST is the result of resolving a SAT and a SIT into a set of viable placement solutions where services are mapped to the infrastructure that is capable of running it.
Each solution can be instantiated as an SI.
The processing consists of three stages: (1) optionally, updating the capabilities of the targets in the SIT, (2) matching the requirements, policies, and capabilities of the SIT and SAT, and  (3) storing the results in a document as a set of actionable solutions.
The SIT is optionally updated by retrieving the current capabilities of each infrastructure target.
After, the SIT is written back as an updated document with the up-to-date capabilities included.
The SIT and SAT are matched through a policy agent which considers the requirements and policies of the SAT with the requirements, policies, and capabilities of the SIT and produces valid mappings.
The end result is the ST as a document that contains the set of mappings of services to the infrastructure.

A SI is the result of picking a solution from the ST and providing it to an orchestration tool for actually creating the application in the IT environment.
The picking of this solution itself can be driven by a policy - such as choosing the solution with the most replica's or lowest latency.

### Example: Stack Template Simple

```json
TODO
```

There are 4 possible SI, one for each target.

```json
TODO
```
