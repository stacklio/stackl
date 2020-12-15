---
title: Extending tools
kind: supported-tools
weight: 5
date: 2020-12-11 01:00:00 +0100
publishdate: 2020-12-11 00:00:00 +0000
expirydate: 2030-12-11 00:00:00 +0000
draft: false
tags: []
---

Extending the existing STACKL toolset can be achieved by creating a `subclass` of the `base-handler` and implementing its abstract methods.

Specifically, every subclass needs to implement the following:

- Class constructor
- create_command_args method
- delete_command_args method

## Handler class

As described above, every handler class consists out of a constructor and two methods. In the constructor we define all the objects we need for our Kubernetes job and in the `create` and `delete` methods we define the arguments we want to pass to the tool for creation and deletion.

### Constructor

The constructor is used to create all the necessary Kubernetes objects used by the base handler. Each object will be described in a subsection.

#### Secret handler

The secret handler is an object of the class `SecretHandler`. This class is an abstract class, so the object has to be a child class of `SecretHandler`. This object is optional, if no secrets are used, a secret handler has no function. [More information about secret handlers.](#TODO)

#### Output

The output object handles output for the handler. For more information, visit [output documentation](#TODO).

#### Environment list

The enviornment list is a dictionary containing environment variables and their values necessary for a handler. These environment variables are added to the Kubernetes job. For example:

```python
self._env_list = {
    "ANSIBLE_INVENTORY_PLUGINS": "/opt/ansible/plugins/inventory",
    "ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED": "True"
}
```

These variables point to the custom STACKL inventory script for Ansible and make sure that when the inventory parsing fails the job also fails.

#### Volumes

Volumes is an array containing dictionaries that define Kubernetes volumes. The following table describes every attribute of the dictionary:

| Variable | Description | Required | Values |
|----------|-------------|----------|--------|
| name | Name of the volume | yes | |
| type | Type of the volume | yes | empty_dir/config_map |
| data | Data to add to the volume. Used in conjunction with `config_map` type | yes, when `type==config_map` | Any dictionary |
| mounth_path | Path to mount the volume to. Each volume is mounted to every container in the job | yes | |
| sub_path | A sub path in the mount path | no | |

For example:

```python
self._volumes = [{
    "name": "inventory",
    "type": "config_map",
    "mount_path": "/opt/ansible/playbooks/inventory/stackl.yml",
    "sub_path": "stackl.yml",
    "data": {
        "stackl.yml": json.dumps(self._secret_handler.stackl_inv)
    }
}]
```

#### Init containers

A list of init containers can be added to a handler. Each init container is a dictionary. The following table describes every attribute of the dictionary:

| Variable | Description | Required |
|----------|-------------|----------|
| name | Name of the init container | yes |
| image | Image for the init container | yes |
| args | Args for the init container command | no |

#### Command

The command for the Kubernetes job. The command together with its arguments defines what a handler needs to do when creating, updating or deleting a stack instance. The command is a list of strings.

For example:

```python
self._command = ["ansible"]
```

### Create command args

`create_command_args` is an abstract method of the `base_handler` class. This method is a property that has no parameters except for `self` and returns a list of strings.

Together with the `command` property of the class, these arguments define what command a Kubernetes job will execute when a stack instance of this type is created.

For example:

```python
@property
def create_command_args(self) -> List[str]:
  self._command_args[0] = f'ansible-playbook \
                          {self.provisioning_parameters["ansible_playbook_path"]} \
                          -v -i /opt/ansible/playbooks/inventory/stackl.yml'
  return self._command_args
```

### Delete command args

As the `create_command_args` method, the `delete_command_args` method is an abstract method of the `base_handler` class. This method is a property that has no parameters except for `self` and returns a list of strings.

For example:

```python
@property
def delete_command_args(self) -> List[str]:
    """The command arguments used in a job to delete something with Ansible
    :return: A list with strings containing shell commands
    :rtype: List[str]
    """
    self._delete_command_args = self.create_command_args
    self._delete_command_args[0] += ' -e state=absent'
    return self._delete_command_args
```
