---
title: Configuration
kind: basic
weight: 4
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

## Docker Configuration table

The following parameters control the STACKL Docker compose deployment in [docker-compose.yml](https://github.com/stacklio/stackl/tree/master/build/example_docker/docker-compose.yaml).

| Parameter | Description | Default |
|------------|------|------|
| `LOGLEVEL` | Set the loglevel | INFO |
| `HOST_MACHINE` | Set the host machine name | stackl-agent |
| `STACKL_AGENT_BROKER` | Set the agent broker type  | Local |
| `STACKL_AGENT_HOST` | Set the agent host and port | stackl-agent:50051 |
| `STACKL_HOST` | Set the STACKL host and port | stackl-rest:80 |
| `STACKL_MESSAGE_CHANNEL` | Set the task message channel type | Redis |
| `STACKL_REDIS_HOST` | Set the Redis host | stackl-redis |
| `STACKL_REDISSENTINELHOST` | Set the Redis sentinel host | stackl-redis |
| `STACKL_STORE` | Set the store type | LFS |
| `STACKL_TASK_BROKER` | Set the task broker type | Custom |

## Helm Configuration table

The following parameters control the STACKL Helm deployment in [values.yaml](https://github.com/stacklio/stackl/tree/master/build/helm/values.yaml).

| Parameter | Description | Default |
|------------|------|------|
| `mode` | Set the deployment mode  | prod |
| `image.pullPolicy` | Set the pull policy for all deployments  | Always |
| `datastore.type` | Set the type of the datastore to use | LFS |
| `task_broker.type` | Set the task broker type | Custom |
| `message_channel.type` | Set the message channel type | Redis |
| `agent_broker.type` | Set the agent_broker type | grpc |
| `stacklrest.image` | Set the image to use for the stackl rest api | stacklio/stackl-rest |
| `stacklrest.name` | Set the name of stackl-rest | stackl-rest |
| `stacklrest.hostname` | Hostname of stackl-rest | stackl.local |
| `stacklrest.replicaCount` | Replicas of stackl-rest | 1 |
| `stacklworker.image` | Set the image to use for stackl-worker | stacklio/stackl-worker:dev |
| `stacklworker.name`| Set the name for stackl-worker | stackl-worker |
| `stacklworker.replicaCount` | Replicas for stackl-worker | 1 |
| `stacklredis.image` | Set the image for redis | redis:5.0.5 |
| `stacklredis.name` | Set the name for redis | stackl-redis |
| `stacklredis.replicaCount` | Replicas for stackl-redis | 1 |
| `stacklagent.image` | Set the mage to use for stackl-agent | stacklio/stackl-agent |
| `stacklagent.name` | Set the name for stackl-agent | stackl-agent |
| `stacklagent.replicaCount` | Replicas for stackl-agent | 1 |
| `imagePullSecrets` | Set the name of image pull secrets to be used by deployments | [name: dome-nexus] |
