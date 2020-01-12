---
title: Agent entities
kind: documentation
weight: 4
---
Agents are software entities that operate locally in the user’s IT environment to manage user-side tasks. Each user has one or more agents that interact with Workers in STACKL. Agents access the automation endpoints that live in the user’s IT infrastructure to do application deployment and management through invocations with the orchestration tools. As such, agents are the user-side actors that provide an authorized end-to-end execution of an IT automation strategy through STACKL and help achieve its autonomous operation guidelines. Thus, Agents have a single main responsibility: receiving, performing, and returning reports on user-side aspects of tasks when given by STACKL workers, such as initiating stack instances on automation endpoints.

## Agent design
Agents are generally deployable software modules that operate in various heterogeneous usert-side IT environments and interact with the local automation endpoints as well as the user’s STACKL deployment. Agents do not necessarily hold state or are active before being needed. Agents understand and work with YAML or JSON formatted files and are able to provide these as Key/Value configuration packets to the relevant automation end-points. Agents interact through a secure and authorized connection with other parties.

Agents are pluggable modules that can operate through different mechanisms as long as they fulfill the above described responsibilities. The type is chosen at deployment time of STACKL. Each agent module needs to provide an implementation of the agent interface through which workers in STACKL can give tasks and receive or retrieve information. Currently, there is a working implementation of an agent as a websocket client and as a GRPC client. A future target is an implementation with gitlab-runners. Other possibilities are other types of scripts, or making agents installable as autonomous ‘pip install’ modules.

### Modules

#### Agent as a python script in a container
Agents are a simple python3 script that are deployed as persistent containers with the STACKL url as environment variable. On start, it  creates a full duplex websocket connection to STACKL and registers its connection info as a websocket connection that STACKL’s workers can use. It runs two permanent asynchronous tasks: (1) the STACKL connection, which can be used to do autonomous reporting on the clients IT state, and (2) a listening websocket to engage in temporary connections with STACKL workers, for instance, during client-side stack instance creation. In theory, (1) could be removed as  agents do not need a permanent connection to STACKL or vice versa.

Currently, the agent is not developed beyond accepting and returning JSON-formatted files as K/V pairs in communication with STACKL and workers. It needs to be able to process these files to connect to and configure the relevant automation endpoints and autonomously monitor and report on the state of the IT infrastructure and applications.  The script is spun up in a container on a machine.

#### Agent as a gitlab-runner

### Design Considerations
Since agents are already in connection with STACKL, they can also form a good point of interaction for the client with STACKL, instead of through the website
This consideration disappears since agents can be stateless entities which are spun up as needed (see runners)
