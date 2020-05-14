---
title: Orchestration Agents
kind: advanced
weight: 4
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

(TODO - this needs a clean rework since it has heavily changed)

Orchestration Agents are software entities that operate at the client to perform actions in their IT environment.
Each environment has one or more agents that interact with workers in STACKL.
Agents have access to the automation endpoints which contain the orchestration tools that execute a workflow in the client's IT infrastructure, for instance to deploy an application.
As client-side actors, they are responsible for receiving, performing, and returning reports on work elements of tasks when given by STACKL workers.

## Orchestration Agent Design

Agents are general software modules that operate in the heterogeneous client-side IT environment and interact with the local automation endpoints as well as with the client's STACKL deployment.
Agents do not necessarily hold state or are continuously active.
Agents understand and work with YAML or JSON-formatted files and are able to provide these as Key/Value configuration packets to automation end-points.
Agents interact through a secure and authorized connection with other parties.

Agents are pluggable modules, chosen during the deployment of STACKL, that can operate through different mechanisms as long as they fulfill the above described responsibilities.
Each agent module needs to provide an implementation of the agent interface through which workers in STACKL can give tasks and receive or retrieve information.
Currently, the supported agent modules are a Docker Agent and a Kubernetes Agent which both support ansible, packer, and terraform as orchestrating tools for the automation endpoints.

See [Agent Interface]({{< ref "../modules/agent_interface.md" >}}) for information about the available modules and how to create your own.
