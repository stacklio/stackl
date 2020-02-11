---
title: Configuration
kind: basic
weight: 4
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
## Configuration table

| Parameter | Description | Default |
|------------|------|------|
| image.pullPolicy | Set the pull policy for all deployments  | Always |
| datastore.type | Set the type of the datastore to use | LFS |
| task_broker.type | Set the task broker type | Custom |
| message_channel.type | Set the message channel type | RedisSingle |
| agent_broker.type | Set the agent_broker type | grpc |
| stacklrest.image | Set the image to use for the stackl rest api | nexus-dockerint.dome.dev/stackl/stackl-rest |
| stacklrest.name | Set the name of stackl-rest | stackl-rest |
| stacklrest.hostname | Hostname of stackl-rest | stackl.local |
| stacklrest.replicaCount | replicas of stackl-rest | 1 |
| stacklworker.image | image to use for stackl-worker | nexus-dockerint.dome.dev/stackl/stackl-worker |
| stacklworker.name | name for stackl-worker | stackl-worker |
| stacklworker.replicaCount | replicas for stackl-worker | 1 |
| stacklredis.image | image for redis | redis:5.0.5 |
| stacklredis.name | name for redis | stackl-redis |
| stacklredis.replicaCount | replicas for stackl-redis | 1 |
| stacklagent.image | Image to use for stackl-agent | nexus-dockerint.dome.dev/stackl/stackl-agent |
| stacklagent.name | Name for stackl-agent | stackl-agent |
| stacklagent.replicaCount | replicas for stackl-agent | 1 |
| imagePullSecrets | name of image pull secrets to be used by deployments | [name: dome-nexus] |
