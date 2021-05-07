---
title: Stackl Stages
kind: advanced
weight: 1
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
To specify in what order services need to run, you can add stages to your Stackl instance.

Stages have a `name` (used as a description) and a `services` field. In `services` you can specify what services you want to run in a certain stage.

## Example

Following example is a Stack instance config file. Using these stages, the `database_service` will be deployed first. Once that service is finished, the `backend_service` and `frontend_service` will be deployed in parallel.

```yaml
---
params:
  key: value
stack_application_template: sat_example
stack_infrastructure_template: sit_example
stages:
- name: eerste-stap
  services:
  - database_service
- name: 2de-stap
  services:
  - backend_service
  - frontend_service
```
