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

## Stackl Core Configuration table

The following environment variables can be set for the stackl-core:

| Parameter | Description | Default |
|------------|------|------|
| `LOG_LEVEL` | Set the loglevel | INFO |
| `STACKL_STORE` | Set the type of stackl store options: Redis/LFS | Redis |
| `STACKL_DATASTORE_PATH` | Path where to safe the stackl documents, only used when `STACKL_STORE` is `LFS` | /lfs-store |
| `STACKL_REDIS_TYPE` | Set the redis type, only change this to `false` for testing | real |
| `STACKL_REDIS_HOST` | The host where redis is running| localhost |
| `STACKL_REDIS_PORT` | The port of the running redis instance | 6379 |
| `STACKL_REDIS_PASSWORD` | Password of the redis instance |  |
| `STACKL_OPA_HOST` | Hostname of the OPA instance | http://localhost:8181 |
| `ELASTIC_APM_ENABLED` | Use this to enable the Elastic APM middleware, configuration can be done by using environment variables, for more information: [APM config](https://www.elastic.co/guide/en/apm/agent/python/current/configuration.html) | False |


## Stackl Agent Configuration table

The following environment variables can be set for the stackl-agent:

### General Settings

| Parameter | Description | Default |
|------------|------|------|
| `STACKL_HOST` | Host where stackl is running | http://localhost:8000 |
| `AGENT_NAME` | Name of the agent | common |
| `AGENT_TYPE` | Type that will be used for executing jobs, choices: kubernetes, docker, mock | mock |
| `REDIS_HOST` | Host of the stackl redis instance | localhost |
| `REDIS_PORT` | Port of the stackl redis instance | 6379 |
| `REDIS_PASSWORD` | Password of the redis instance |  |
| `SECRET_HANDLER` | The secret handler to use, choices: base64, vault, conjur | base64 |
| `LOGLEVEL` | The loglevel for the agent, Choices: DEBUG, INFO, ERROR, WARN | INFO |
| `STACKL_CLI_IMAGE` | The image used for sending outputs back to stackl | stacklio/stackl-cli |
| `MAX_JOBS` | The maximum amount of jobs that can be run in parallel | 10 |
| `JOB_TIMEOUT` | Time until a job times out. When this timeout is exceeded, the status of a kubernetes job is not tracked anymore | 3660 |

### Kubernetes Handler

| Parameter | Description | Default |
|------------|------|------|
| `STACKL_NAMESPACE` | The namespace where automation jobs will be ran  | |
| `SERVICE_ACCOUNT` | The kubernetes service account that will be used for jobs | |

### Vault Secret Handler

| Parameter | Description | Default |
|------------|------|------|
| `VAULT_ROLE` | vault role to be used by vault-agent | |
| `VAULT_ADDR` | hostname/ip where vault is running | |
| `VAULT_MOUNT_POINT` | The kubernetes auth method vault path, for more information: https://www.vaultproject.io/docs/auth/kubernetes#authentication | |

### Conjur Secret Handler

| Parameter | Description | Default |
|------------|------|------|
| `AUTHENTICATOR_CLIENT_CONTAINER_NAME` | The Conjur container name | |
| `CONJUR_APPLIANCE_URL` | Url of the Conjur appliance | |
| `CONJUR_AUTHN_TOKEN_FILE` | Filename where the token will be saved | |
| `CONJUR_AUTHN_URL` | The Conjur authentication URL | |
| `CONJUR_AUTHN_LOGIN` | Authn login path in Conjur | |
| `CONJUR_SSL_CONFIG_MAP` | Configmap where the SSL cert is | |
| `CONJUR_SSL_CONFIG_MAP_KEY` | Key in the configmap of the SSL cert | |
| `CONJUR_VERIFY` | Verify Ssl, Choices: True, False | |