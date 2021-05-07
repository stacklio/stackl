---
title: Service Policies
kind: advanced
weight: 10
date: 2021-04-22 01:00:00 +0100
publishdate: 2021-04-22 01:00:00 +0100
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
Service policies can be used to apply an OPA policy to a specific service.

## Example

The following example provides a way to skip certain functional requirements.

In this scenario, the service's goal is to deploy a database. In this example, this can be achieved in different ways. For VMware, we first deploy a VM using Terraform, then configure database software on the deployed VM. On AWS however, we decide to use an AWS SaaS solution to achieve the same result.

This means we don't want to deploy a VM using terraform/use Ansible for configuration on AWS, and vice versa. To achieve this, we have written the following policy, which filters out certain functional requirements based on the `cloud_provider`.

```yaml
category: configs
description: skiponprovider
name: skiponprovider
type: policy_template
inputs: [cloud_provider, functional_requirements]
outputs: []
policy: |
  package skiponprovider
  default filter = {x | x := input.functional_requirements[_]}
  filter = frs {
    service := input.service
    input.stack_instance.services[service][service_target].infrastructure_target == input.infrastructure_target
    input.stack_instance.services[service][service_target].cloud_provider == input.inputs.cloud_provider
    frs := {x | x := input.functional_requirements[_]} - {y | y := input.inputs.functional_requirements[_]}
  }
```

The following service example uses the policy to filter out functional requirements based on the `cloud_provider` (a parameter added in an `environment`, `location` or `zone`).

```yaml
name: service_skip_example
type: service
category: items
description: service_skip_example
functional_requirements:
  - terraform_vm
  - db_ansible
  - aws_db
params: {}
resource_requirements: null
service_policies:
  - name: skiponprovider
    inputs: 
      cloud_provider: aws
      functional_requirements:
        - terraform_vm
        - db_ansible
  - name: skiponprovider
    inputs: 
      cloud_provider: vmw
      functional_requirements:
        - aws_db
```
