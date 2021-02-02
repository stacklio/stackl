---
title: Introduction
kind: supported-tools
weight: 1
date: 2020-12-11 01:00:00 +0100
publishdate: 2020-12-11 00:00:00 +0000
expirydate: 2030-12-11 00:00:00 +0000
draft: false
tags: []
---

STACKL supports a number of tools to perform automation. At the moment these tools are:

- Ansible
- Terraform
- Packer

Every tool has it's own `handler` in the STACKL-agent. Each of these handler extends the `base-handler` and implements its abstract methods. This provides an easy way for a developer to extend STACKL with a new tool.

The `base-handler` for Kubernetes has the task of creating a Kubernetes job, with the given parameters from the child class. For example: the Ansible handler adds a volume mount for the Ansible inventory script. The base handler will create a config map for this inventory script and will mount it in the Kubernetes job.

The base handler also has the responsibility of checking the status of a pod created by the Kubernetes job. If a pod fails, the logs will be put into the `Stack instance` by the base handler.
