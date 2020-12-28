---
title: Policy Engine
kind: policies
weight: 1
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

## Stack orchestration

STACKL works through modelling the IT environment through SITs, including infrastructure capabilities and additional requirements (i.e., policies) and describing applications through SATs, which specify services and their functional, resource and policy requirements.
Accordingly, this is a natural match to what a policy engine needs: rules (i.e., policies) and data to reason over.

Thus, STACKL uses OPA for stack orchestration through:

- Providing OPA with default policies that model standard requirements for any SIT and SAT placement solution
- Extracting additional policies from the SIT and SAT and providing these to OPA as well
- Extracting the modeling and description data of the SIT and SAT
- Querying OPA for placement solutions for the data with all the policies
- Storing the resulting policy decision as a set of placement solutions in a ST

