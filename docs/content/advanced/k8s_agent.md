---
title: Kubernetes Agents
kind: advanced
weight: 4
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

Kubernetes agents are [agents](agents.md) designed to work on a Kubernetes cluster. 

## Base agent

The base agent is an abstract class. This class's functionality is to create a Kubernetes job using 
the properties defined in the child class. Each child class can override the following properties to alter the Pod spec:

| Property | Description | Type |
|----------|-------------|------|
| env_list | A list of environment variables to be added to the Pod. | Dict |
| volumes | Volumes to be added to the pod. All volumes in this list will be mounted to all containers in the pod. The list must be a list of dicts. Each dict can contain the following variables: | List of dicts |
| init_containers | A list of init containers to be added. | List of dicts |
| command | Command to be executed by the job. | String |
| command_args | Args passed to the command of the job. | List of strings |

### Volumes

The volumes property must be a list of dicts. The following keys can be used in the dict:

| Key | Required | Description | Options |
|-----|----------|-------------|---------|
| name | yes | Name of the volume. | |
| type | yes | Type of volume. | config_map, empty_dir |
| mount_path | yes | Path where to mount volume. | |
| data | Required when type == "config_map" | Dict containing config_map data. | |

### Init containers

The init containers property must be a list of dicts. The following keys can be used in the dict:

| Key | Required | Description |
|-----|----------|-------------|
| name | yes | Name of the container. |
| image | yes | Image of the container. |
| args | yes | Args to add to the init container command. List of strings |

## Ansible handler

The Ansible handler is used to execute Ansible roles using Stackl.

Variables from Stackl are added as host variables to the role via a dynamic inventory script. This script also has the capability to read secrets from Vault and add them as host variables.

For this to work, `hvac` and `stackl-client` pypi packages are required.

### Example

Using `stackl-cli`, an Ansible role can be executed using the following command:

```
stackl create instance --stack-application-template <sat_name> --stack-infrastructure-template <sit_name> <stack_instance_name>
```

## Terraform handler

The Terraform handler is used to execute Terraform plans using Stackl.

Variables from Stackl are added to a config map and mounted in the Terraform container. Secrets from Vault are read using an init container and templated to a JSON file. This file is then added to the Terraform container.

### Example

```
stackl create instance --stack-application-template <sat_name> --stack-infrastructure-template <sit_name> <stack_instance_name>
```

## Packer handler

The Packer handler is used to execute Packer builds using Stackl.

Variables from Stackl are added to a config map and mounted in the Packer container. Secrets from Vault are read using an init container and templated to a JSON file. This file is then added to the Packer container.

### Example

```
stackl create instance --stack-application-template <sat_name> --stack-infrastructure-template <sit_name> <stack_instance_name>
```

## References

* [Dynamic inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html)
