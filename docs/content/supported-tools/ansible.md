---
title: Ansible
kind: supported-tools
weight: 2
date: 2020-12-11 01:00:00 +0100
publishdate: 2020-12-11 00:00:00 +0000
expirydate: 2030-12-11 00:00:00 +0000
draft: false
tags: []
---

## Execution

By default Stackl tries to execute an Ansible role [ad-hoc](https://docs.ansible.com/ansible/latest/user_guide/intro_adhoc.html).

```python
f'ansible {pattern} -m include_role -v -i /opt/ansible/playbooks/inventory/stackl.yml -a name={self._functional_requirement}'
```

### Ad-hoc

#### Pattern

The [pattern](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html) is the pattern used to target hosts or groups. This pattern is either the Stackl [hosts](#Hosts) or the name of the `Stackl service` plus its index.

### Hosts

Hosts can be defined in multiple ways:

- Policy driven: SAT policy to define hostnames
- Ansible groups defined in the provisioning parameters of the Stackl Instance
- Default implicit `"localhost"`

#### Policy driven

A policy can be defined to create hostnames for objects in a Stack Instance. For example:

```yaml
---
category: configs
description: naming policy
name: naming
type: policy_template
inputs: []
outputs: [stackl_hostname]
policy: |
  package naming

  solutions = {"fulfilled": true, "targets": targets} {
    service_params := input.services[input.parameters.service].params

    targets := [{"target": it, "stackl_hostname": stackl_hostname} |
      infra_target_params := input.infrastructure_targets[it].params
      domain_letters := infra_target_params.domain_letters
      server_type_letters := service_params.server_type_letters
      os := substring(service_params.operating_system, 0, 1)
      index_number := "{counter(prod_counter, 8000)}"

      stackl_hostname := sprintf("%v%v%v%v", [domain_letters, server_type_letters, os, index_number])
    ]
    count(targets) > 0
  }

  else = {"fulfilled": false, "msg": msg} {
    msg := "No target with all required fields for naming convention"
  }
```

This policy creates a hostname for each of the instances in a Stackl Instance and outputs the result to a specific `hosts` field in the Stack Instance. When executing Ansible for a Stack Instance with the hosts field filled out, Stackl will use these `hosts` as the `pattern` for the job.

#### Ansible groups defined in Stack Instance

Desired Ansible groups can be defined in a Stack Instance. Following variables are used to define groups using a Stack Instance:

- default_inventory_group: Default group for instance when instances > amount of groups
- stackl_inventory_groups: Dictionary containing desired group configuration
- instances: Number of `instances` in Stack Instance
- stackl_hostname: Template for the hostname

```yaml
---
params:
  default_inventory_group: nodes
  stackl_inventory_groups:
    - tags: ["master"]
      description: ""
      count: 1
    - tags: ["etcd", "master"]
      description: ""
      count: 2
  instances: 3
  stackl_hostname: "group_test_{hi}"
```

This example will result in an Ansible inventory made up of 3 hosts. 3 of these hosts will be grouped under `master` and 2 will be grouped under `etcd`. For more information, view the [Ansible inventory](#ansible-inventory) chapter.

#### Default implicit localhost

By default Stackl has no actual hosts and will run with connection local. Variables are grouped under a hosts named after the service. For example:

```json
{
    "_meta": {
        "hostvars": {
            "example_service_0": {
                "key": "value",
                "..."
            }
        }
    },
    "all": {
        "children": [
            "example_service",
            "ungrouped"
        ]
    },
    "example_service": {
        "hosts": [
            "example_service_0"
        ]
    }
}
```

Here all variables are placed under host `example_service_0`. `example_service` is the name of the service used in this example. The 0 at the end is the index. Using multiple replicas increases this index.

### Playbook execution

To execute a playbook with the Ansible handler, add a playbook to the OCI image and add a variable called `ansible_playbook_path` to the Stack Instance.

For example:

```yaml
---
- name: update web servers
  hosts: localhost
  connection: local

  tasks:
  - name: ensure apache is at the latest version
    debug:
      msg: installing latest apache version

  - name: write the apache config file
    debug:
      msg: writing apache version

- name: update db servers
  hosts: localhost
  connection: local

  tasks:
  - name: ensure postgresql is at the latest version
    debug:
      msg: installing latest postgresql version
  - name: ensure that postgresql is started
    debug:
      msg: start postgresql service
```

To execute this playbook, add `ansible_playbook_path` to the stack instance. This can be done either by adding the variable to the instance itself or to any other document used by the instance (for example the functional requirment).

```yaml
category: configs
description: example-playbook
invocation:
  generic:
    description: Example playbook
    image: stacklio/example-playbook:v1.0.0
    tool: ansible
name: example-playbook
params:
  ansible_playbook_path: /opt/ansible/playbook.yml
type: functional_requirement
```

Creating a stack instance using this functional requirement will execute the playbook. Example logs:

```bash
PLAY [update web servers] ******************************************************
TASK [Gathering Facts] *********************************************************
ok: [localhost]
TASK [ensure apache is at the latest version] **********************************
ok: [localhost] => {
    "msg": "installing latest apache version"
}
TASK [write the apache config file] ********************************************
ok: [localhost] => {
    "msg": "writing apache version"
}
PLAY [update db servers] *******************************************************
TASK [Gathering Facts] *********************************************************
ok: [localhost]
TASK [ensure postgresql is at the latest version] ******************************
ok: [localhost] => {
    "msg": "installing latest postgresql version"
}
TASK [ensure that postgresql is started] ***************************************
ok: [localhost] => {
    "msg": "start postgresql service"
}
PLAY RECAP *********************************************************************
localhost                  : ok=6    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Ansible inventory

{{< figure src="stackl-inventory.png" caption="Stackl Ansible Inventory" >}}

Using the example in one of the previous chapters, let's look closer at how Ansible Inventory is build using Stackl.

### Requirements

- [stackl-client](#TODO)

### Groups

```yaml
---
params:
  default_inventory_group: nodes
  stackl_inventory_groups:
    - tags: ["master"]
      description: ""
      count: 1
    - tags: ["etcd", "master"]
      description: ""
      count: 2
  instances: 3
  stackl_hostname: "group_test_{hi}"
```

In this example, we have three instances. One of those instances should only be in the `master` group, the other two should be in the `etcd` and `master` group.

On first execution (creation of the Stack Instance) these groups are created by the [Stackl Ansible inventory script](#Inventory). When a Stack Instance is updated, the created groups are evaluated to make sure the existing groups still match the desired state as described in the Stack Instance. If not, an update to the group is made. If the desired state is not possible given the configuration, an error is thrown.

To view the inventory from this Stack Instance, run `ansible-inventory -i stackl.yml --list` with the following `stackl.yml` file:

```yaml
---
plugin: stackl
host: https://stackl.example.com
stack_instance: stack-instance-name
secret_handler: base64
```

This results in the following inventory:

```json
{
    "_meta": {
        "hostvars": {
            "group_test_01": {
                "key": "value",
                "..."
            },
            "group_test_02": {
                "key": "value",
                "..."
            },
            "group_test_03": {
                "key": "value",
                "..."
            }
        }
    },
    "all": {
        "children": [
            "etcd",
            "master",
            "ungrouped"
        ]
    },
    "etcd": {
        "hosts": [
            "group_test_02",
            "group_test_03"
        ]
    },
    "master": {
        "hosts": [
            "group_test_01",
            "group_test_02",
            "group_test_03"
        ]
    }
}
```

### Stackl Instance Variables and Secrets

All Stackl Instance variables are placed under the host. For example:

```json
{
    "_meta": {
        "hostvars": {
            "example_service_0": {
                "ansible_connection": "local",
                "app": "container-deployment",
                "environment": "development",
                "hostname": "container-deployment",
                "image_name": "nginx",
                "image_tag": "latest",
                "infrastructure_target": "example.infra.k8s",
                "livenessprobe_port": 80,
                "microservice_port": 80,
                "namespace": "namespace",
                "readinessprobe_port": 80
            }
        }
    },
    "all": {
        "children": [
            "example_service",
            "ungrouped"
        ]
    },
    "example_service": {
        "hosts": [
            "example_service_0"
        ]
    }
}
```

When defined, secrets are also added as host variables. For secrets to work in Stackl's Ansible Inventory, the inventory script will need some extra variables, depending on the Secret Handler. For more information, visit the [Inventory documentation](#TODO).

## References

- [Ansible ad-hoc](https://docs.ansible.com/ansible/latest/user_guide/intro_adhoc.html)
- [Ansible playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html)
- [Ansible pattern](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html)
- [Ansible dynamic inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html)
