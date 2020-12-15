---
title: Agent Interface
kind: modules
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: true
tags: []
---

(TODO - this needs a clean rework since it has heavily changed)

Agents are pluggable modules, chosen during the deployment of STACKL, that can operate through different mechanisms as long as they fulfill the above described responsibilities.
Each agent module needs to provide an implementation of the agent interface through which workers in STACKL can give tasks and receive or retrieve information.
Currently, there is a working implementation of an agent as a websocket client and as a GRPC client.
A future target is an implementation with gitlab-runners.
Other possibilities are other types of scripts, or making agents installable as autonomous 'pip install' modules.

## Agent as a python script in a container using websockets

Agents are a simple python3 script that are deployed as persistent containers with the STACKL url as environment variable.
On start, it  creates a full duplex websocket connection to STACKL and registers its connection info as a websocket connection that STACKL's workers can use.
It runs two permanent asynchronous tasks: (1) the STACKL connection, which can be used to do autonomous reporting on the clients IT state, and (2) a listening websocket to engage in temporary connections with STACKL workers, for instance, during client-side stack instance creation.
In theory, (1) could be removed as  agents do not need a permanent connection to STACKL or vice versa.

Currently, the agent is not developed beyond accepting and returning JSON-formatted files as K/V pairs in communication with STACKL and workers.
It needs to be able to process these files to connect to and configure the relevant automation endpoints and autonomously monitor and report on the state of the IT infrastructure and applications.
The script is spun up in a container on a machine.

## Agent as a python script in a container using GRPC

TODO Work-in-Progress

### Agent as a gitlab-runner

TODO Work-in-Progress

<!-- Samy:
Een beetje meer uitleg van waar het idee komt om Gitlab runners te gebruiken als proxies initieel.(in plaats dat de connectie gebeurt met websockets is het via de GitLab API)
de proxy is momenteel geschreven in Python met libraries welke niet meer maintained zijn, deze zou herschreven moeten worden in Python of Golang.
De functionele requirements zijn
- connecties leggen met Stackl met een http proxy
- live volgen van logs van de deployment
- per invocation een pod aanmaken op Kubernetes, deze volgen(zie logs hierboven) en daarna verwijderen(met jobs zou dit automatisch kunnen gebeuren misschien)
- update playbook om de proxy op te zetten
- update container image van de proxy
- ondersteuning proxy tag om individuele proxies te selecteren
Voor GitLab runners hebben we dit allemaal al:
- logs met filebeat
- kubernetes executor maakt pods aan
- ondersteunt http proxies
- ondersteuning runner tags om individuele proxies te selecteren
- playbook voor deployment van Gitlab Runner en Gitlab
wat extra geschreven zou moeten worden is de proxy interface en de implementatie voor GitLab die de Gitlab API aanspreken(create project from skeleton, run pipeline with variables https://docs.gitlab.com/ee/api/pipelines.html#create-a-new-pipeline ) -->
