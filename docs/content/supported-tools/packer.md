---
title: Packer
kind: supported-tools
weight: 4
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

The Packer handler is used to execute Packer builds using Stackl.

Variables from Stackl are added to a config map and mounted in the Packer container. Secrets from Vault are read using an init container and templated to a JSON file. This file is then added to the Packer container.

### Example

```bash
stackl create instance --stack-application-template <sat_name> --stack-infrastructure-template <sit_name> <stack_instance_name>
```
