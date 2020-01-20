---
title: Agents
kind: advanced
weight: 4
---

Agents are software entities that operate in the user’s IT environment to manage parts of tasks that are user-side.
Each user has one or more agents that interact with workers in STACKL.
Agents have access to the automation endpoints which contain the orchestration tools that execute a workflow in the user’s IT infrastructure, for instance to deploy an application.
As user-side actors, they are responsible for receiving, performing, and returning reports on user-side work elements of tasks when given by STACKL workers.

## Agent Design

Agents are general software modules that operate in the heterogeneous user-side IT environment and interact with the local automation endpoints as well as with the user’s STACKL deployment.
Agents do not necessarily hold state or are continuously active.
Agents understand and work with YAML or JSON formatted files and are able to provide these as Key/Value configuration packets to the relevant automation end-points.
Agents interact through a secure and authorized connection with other parties.

Agents are pluggable modules, chosen during the deployment of STACKL, that can operate through different mechanisms as long as they fulfill the above described responsibilities.
Each agent module needs to provide an implementation of the agent interface through which workers in STACKL can give tasks and receive or retrieve information.
Currently, there is a working implementation of an agent as a websocket client and as a GRPC client.
A future target is an implementation with gitlab-runners.
Other possibilities are other types of scripts, or making agents installable as autonomous ‘pip install’ modules.

See [Agent Interface]({{< ref "../modules/agent_interface.md" >}}) for information about the available modules and how to create your own.
