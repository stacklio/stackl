---
title: Outputs
kind: supported-tools
weight: 7
date: 2020-12-11 01:00:00 +0100
publishdate: 2020-12-11 00:00:00 +0000
expirydate: 2030-12-11 00:00:00 +0000
draft: false
tags: []
---

Outputs can be used to add a variable from the execution of automation code to the Stack Instance. This is achieved by adding a sidecar container to the Kubernetes job. The sidecar container and job container share an [empty dir volume](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir). The sidecar container waits for a file to be written to the volume and then uses a JSON converter to look for the variable to be added to the Stack Instance. Once it is added to the Stack Instance, other services can make use of this variable. Outputs can be added to any Functional Requirement of type Terraform or Ansible.

## Example

```yaml
...
outputs:
  ip_address: ip_address
...
```

This example adds the `ip_address` variable value to the Stack Instance. 

## References

- [Kubernetes empty dir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)