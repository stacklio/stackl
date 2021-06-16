"""
Module for handling invocation with Ansible
"""
import json
import os
from typing import List
from agent.kubernetes.handlers.ansible_plugins.inventory import STACKL_PLUGIN
from agent.kubernetes.handlers.ansible_plugins.callback import ANSIBLE_CALLBACK_PLUGIN

from agent.kubernetes.kubernetes_secret_factory import get_secret_handler

from .base_handler import Handler

PLAYBOOK_INCLUDE_ROLE = """
- hosts: "{{ pattern }}"
  serial: "{{ stackl_serial }}"
  connection: "{{ stackl_connection }}"
  gather_facts: "{{ stackl_gather_facts }}"
  become: "{{ stackl_become }}"
  pre_tasks:
    - wait_for_connection:
      when: stackl_wait_for_connection is defined
  tasks:
    - include_role:
        name: "{{ ansible_role }}"
"""


class AnsibleHandler(Handler):
    """Handler for functional requirements using the 'ansible' tool
Example invoc:
class Invocation():
    def __init__(self):
        self.image = "ansible_example"
        self.infrastructure_target = "vsphere.brussels.vmw-vcenter-01"
        self.stack_instance = "instance-1"
        self.service = "windows2019"
        self.functional_requirement = "windows2019"
        self.tool = "ansible"
        self.action = "create"
"""
    def __init__(self, invoc):
        super().__init__(invoc)
        self._secret_handler = get_secret_handler(invoc, self._stack_instance,
                                                  "yaml")
        self._env_list = {
            "ANSIBLE_INVENTORY_PLUGINS": "/opt/ansible/plugins/inventory",
            "ANSIBLE_CALLBACK_PLUGINS":
            "/opt/ansible/plugins/callback_plugins",
            "ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED": "True",
            "STACKL_INFRASTRUCTURE_TARGET": self._invoc.infrastructure_target,
            "STACKL_FUNCTIONAL_REQUIREMENT": self._functional_requirement,
            "STACKL_SERVICE": self._service,
            "STACKL_STACK_INSTANCE": self._invoc.stack_instance,
            "STACKL_URL": os.environ.get("STACKL_HOST", "http://stackl:8080")
        }
        """ Volumes is an array containing dicts that define Kubernetes volumes
        volume = {
            name: affix for volume name, str
            type: 'config_map' or 'empty_dir', str
            data: dict with keys for files and values with strings, dict
            mount_path: the volume mount path in the automation container, str
            sub_path: a specific file in the volume, str
        }
        """
        self._volumes = [{
            "name": "inventory",
            "type": "config_map",
            "mount_path": "/opt/ansible/playbooks/inventory/stackl.yml",
            "sub_path": "stackl.yml",
            "data": {
                "stackl.yml": json.dumps(self._secret_handler.stackl_inv)
            }
        }, {
            "name": "stackl-plugin",
            "type": "config_map",
            "mount_path": "/opt/ansible/plugins/inventory/stackl.py",
            "sub_path": "stackl.py",
            "data": {
                "stackl.py": STACKL_PLUGIN
            }
        }, {
            "name": "stackl-callback-plugin",
            "type": "config_map",
            "mount_path": "/opt/ansible/plugins/callback_plugins/stackl.py",
            "sub_path": "stackl.py",
            "data": {
                "stackl.py": ANSIBLE_CALLBACK_PLUGIN
            }
        }, {
            "name": "stackl-playbook",
            "type": "config_map",
            "mount_path": "/opt/ansible/playbooks/stackl/",
            "data": {
                "playbook-role.yml": PLAYBOOK_INCLUDE_ROLE
            }
        }]
        # If any outputs are defined in the functional requirement set in base_handler

        self._init_containers = []

    @property
    def create_command_args(self) -> List[str]:
        """The command arguments used in a job to create something with Ansible

        :return: A list with strings containing shell commands
        :rtype: List[str]
        """
        if self._invoc.playbook_path:
            ansible_commands = [
                'ansible-playbook', self._invoc.playbook_path, '-v', '-i',
                '/opt/ansible/playbooks/inventory/stackl.yml'
            ]

        else:
            if self.hosts:
                pattern = ",".join(self.hosts)
            else:
                pattern = self._service + "_" + str(self.index)

            if self._invoc.ansible_role:
                ansible_role = self._invoc.ansible_role
            else:
                ansible_role = self._functional_requirement

            ansible_commands = [
                'ansible-playbook', '/opt/ansible/playbooks/stackl/playbook-role.yml', '-i',
                '/opt/ansible/playbooks/inventory/stackl.yml', '-e', f'pattern={pattern}', '-e', f'ansible_role={ansible_role}',
                '-e', f'stackl_serial={self._invoc.serial}', '-e', f'stackl_gather_facts={self._invoc.gather_facts}'
            ]

            if self._invoc.wait_for_connection:
                ansible_commands.extend(['-e', f'stackl_wait_for_connection={self._invoc.wait_for_connection}'])

            if self._invoc.become:
                ansible_commands.extend(['-e', f'stackl_become={self._invoc.become}'])
            
            if self._invoc.connection:
                ansible_commands.extend(['-e', f'stackl_connection={self._invoc.connection}'])

            ansible_commands.extend(['-e', f'state=present'])
        return ansible_commands

    @property
    def delete_command_args(self) -> List[str]:
        """The command arguments used in a job to delete something with Ansible

        :return: A list with strings containing shell commands
        :rtype: List[str]
        """
        delete_command_args = self.create_command_args
        delete_command_args.extend(['-e', 'state=absent'])
        return delete_command_args
