---
title: Agent Interface
kind: modules
weight: 4
---

## Agent as a python script in a container using websockets

Agents are a simple python3 script that are deployed as persistent containers with the STACKL url as environment variable. On start, it  creates a full duplex websocket connection to STACKL and registers its connection info as a websocket connection that STACKL’s workers can use. It runs two permanent asynchronous tasks: (1) the STACKL connection, which can be used to do autonomous reporting on the clients IT state, and (2) a listening websocket to engage in temporary connections with STACKL workers, for instance, during client-side stack instance creation. In theory, (1) could be removed as  agents do not need a permanent connection to STACKL or vice versa.

Currently, the agent is not developed beyond accepting and returning JSON-formatted files as K/V pairs in communication with STACKL and workers. It needs to be able to process these files to connect to and configure the relevant automation endpoints and autonomously monitor and report on the state of the IT infrastructure and applications.  The script is spun up in a container on a machine.

## Agent as a python script in a container using GRPC

Work-in-Progress

### Agent as a gitlab-runner

Work-in-Progress
