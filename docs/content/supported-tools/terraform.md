---
title: Terraform
kind: supported-tools
weight: 4
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

The Terraform handler is used to execute Terraform plans using Stackl.

Variables from Stackl are added to a config map and mounted in the Terraform container. Secrets from Vault are read using an init container and templated to a JSON file. This file is then added to the Terraform container.

## Terraform Backend

In this section we describe how to create a Terraform backend config using Vault.

## Create the backend config in Vault

To add the backend config to Vault you can use `vault-cli`. For example:

`vault kv put secret/terraform-backend <@file>`

With the file:

```json
{
  "terraform": {
    "backend": {
      "s3": {
        "region": "<region>",
        "bucket": "<bucket-name>",
        "access_key": "<access_key>",
        "secret_key": "<secret_key>"
      }
    }
  }
}
```

## Add a secret to your configuration

Add this secret to any document that uses Terraform. 

```yaml
...
secrets:
  backend_secret_path: secret/data/terraform-backend
```

Make sure the secret is called `backend_secret_path`. This way the handler knows which Vault secret to use as a Terraform backend.

The key for the Terraform statefile is added during the job. The name of the key is equal to the stack instance name.

## Example

```bash
stackl create instance --stack-application-template <sat_name> --stack-infrastructure-template <sit_name> <stack_instance_name>
```
