from os import environ
from typing import List

import yaml

from .base_handler import Handler
from agent.kubernetes.secrets.base64_secret_handler import Base64SecretHandler
from agent.kubernetes.secrets.vault_secret_handler import VaultSecretHandler
from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.outputs.ansible_output import AnsibleOutput

from ..secrets.conjur_secret_handler import ConjurSecretHandler

stackl_plugin = """
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
DOCUMENTATION = '''
name: stackl
plugin_type: inventory
author:
  - Stef Graces <@stgrace>
  - Frederic Van Reet <@GBrawl>
  - Samy Coenen <@samycoenen>
short_description: Stackl inventory
description:
  - Fetch a Stack instance from Stackl.
  - Uses a YAML configuration file that ends with C(stackl.(yml|yaml)).
options:
  plugin:
      description: Name of the plugin
      required: true
      choices: ['stackl']
  host:
      description: Stackl's host url
      required: true
  stack_instance:
      description: Stack instance name
      required: true
  secret_handler:
      description: Name of the secret handler
      required: false
      default: base64
      choices: 
        - vault
        - base64
        - conjur
  vault_addr:
      description: Vault Address
      required: false
  vault_token_path:
      description: Vault token path
      required: false
  conjur_addr:
      description: Conjur Address
      required: false
  conjur_account:
      description: Conjur account
      required: false
  conjur_token_path:
      description: Conjur token path
      required: false
  conjur_verify:
      description: Conjur verify
      default: True
'''
EXAMPLES = '''
plugin: stackl
host: "http://localhost:8080"
stack_instance: "test_vm"
'''
import json
import hvac
import stackl_client
import base64
import requests
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin
from collections import defaultdict


def check_groups(stackl_groups, stackl_inventory_groups, host_list):
    count_group_dict = defaultdict(int)
    target_count = len(host_list)
    for group in stackl_inventory_groups:
        for tag in group['tags']:
            count_group_dict[tag] += group['count']

    for tag, count in count_group_dict.items():
        if not tag in stackl_groups or not len(
                stackl_groups[tag]) == count * target_count:
            return False
    return True


def create_groups(hosts, stackl_inventory_groups):
    groups = defaultdict(list)
    for item in stackl_inventory_groups:
        for tag in item["tags"]:
            for index in range(item["count"]):
                for target, host_list in hosts.items():
                    try:
                        host = stackl_client.HostTarget(target=target,
                                                        host=host_list[index])
                    except IndexError as e:
                        print(e)
                        exit(1)
                    groups[tag].append(host)
        for target in hosts:
            del hosts[target][0:item["count"]]
    return groups


def get_vault_secrets(service, address, token_path):
    f = open(token_path, "r")
    token = f.readline()
    client = hvac.Client(url=address, token=token)
    secret_dict = {}
    for _, value in service.secrets.items():
        secret_value = client.read(value)
        for key, value in secret_value['data']['data'].items():
            secret_dict[key] = value
    return secret_dict


def get_base64_secrets(service):
    secrets = service.secrets
    decoded_secrets = {}
    for key, secret in secrets.items():
        try:
            decoded_secrets[key] = base64.b64decode(secret + "===").decode(
                "utf-8").rstrip()
        except Exception:
            raise AnsibleParserError("Could not decode secret")
    return decoded_secrets


def get_conjur_secrets(service, address, account, token_path, verify):
    with open(token_path) as token_file:
        token = json.load(token_file)
    if isinstance(verify, str) and verify.lower() == "false":
        verify = False
    elif isinstance(verify, str) and verify.lower() == "true":
        verify = True

    token = json.dumps(token).encode('utf-8')
    secrets = service.secrets
    conjur_secrets = {}
    for key, secret_path in secrets.items():
        path = secret_path.split("!var")[1].strip()
        r = requests.get(
            f"{address}/secrets/{account}/variable/{path}",
            headers={
                'Authorization':
                f'Token token=\"{base64.b64encode(token).decode("utf-8")}\"'
            },
            verify=verify)
        conjur_secrets[key] = r.text
    return conjur_secrets


class InventoryModule(BaseInventoryPlugin):
    NAME = 'stackl'

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('stackl.yaml', 'stackl.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            self.plugin = self.get_option('plugin')
            configuration = stackl_client.Configuration()
            configuration.host = self.get_option("host")
            api_client = stackl_client.ApiClient(configuration=configuration)
            api_instance = stackl_client.StackInstancesApi(
                api_client=api_client)
            stack_instance_name = self.get_option("stack_instance")
            stack_instance = api_instance.get_stack_instance(
                stack_instance_name)
            for service, si_service in stack_instance.services.items():
                for index, service_definition in enumerate(si_service):
                    # self.inventory.add_host(host=service + "_" + str(index),
                    #                         group=service)
                    # self.inventory.set_variable(
                    #     service, "infrastructure_target",
                    #     service_definition.infrastructure_target)
                    if hasattr(
                            stack_instance, "hosts"
                    ) and 'stackl_inventory_groups' in service_definition.provisioning_parameters:
                        if not check_groups(
                                stack_instance.groups,
                                service_definition.provisioning_parameters[
                                    'stackl_inventory_groups'],
                                stack_instance.hosts):
                            stack_instance.groups = create_groups(
                                stack_instance.hosts,
                                service_definition.provisioning_parameters[
                                    'stackl_inventory_groups'])
                            stack_update = stackl_client.StackInstanceUpdate(
                                stack_instance_name=stack_instance.name,
                                params={
                                    "stackl_groups": stack_instance.groups
                                },
                                disable_invocation=True)
                            api_instance.put_stack_instance(stack_update)
                        for item, value in stack_instance.groups.items():
                            for group in value:
                                if group.target == service_definition.infrastructure_target:
                                    self.inventory.add_group(item)
                                    self.inventory.add_host(host=group.host,
                                                            group=item)
                                    for key, value in service_definition.provisioning_parameters.items(
                                    ):
                                        self.inventory.set_variable(
                                            item, key, value)
                                    if hasattr(service_definition, "secrets"):
                                        if self.get_option(
                                                "secret_handler") == "vault":
                                            secrets = get_vault_secrets(
                                                service_definition,
                                                self.get_option("vault_addr"),
                                                self.get_option(
                                                    "vault_token_path"))
                                        elif self.get_option(
                                                "secret_handler") == "base64":
                                            secrets = get_base64_secrets(
                                                service_definition)
                                        elif self.get_option("secret_handler") == "conjur":
                                            secrets = get_conjur_secrets(
                                                service_definition,
                                                self.get_option("conjur_addr"),
                                                self.get_option("conjur_account"),
                                                self.get_option("conjur_token_path"),
                                                self.get_option("conjur_verify"))
                                        for key, value in secrets.items():
                                            self.inventory.set_variable(
                                                item, key, value)
                    else:
                        self.inventory.add_group(service)
                        self.inventory.add_host(host=service + "_" +
                                                str(index),
                                                group=service)
                        self.inventory.set_variable(
                            service, "infrastructure_target",
                            service_definition.infrastructure_target)
                        for key, value in service_definition.provisioning_parameters.items(
                        ):
                            self.inventory.set_variable(service, key, value)
                        if hasattr(service_definition, "secrets"):
                            if self.get_option("secret_handler") == "vault":
                                secrets = get_vault_secrets(
                                    service_definition,
                                    self.get_option("vault_addr"),
                                    self.get_option("vault_token_path"))
                            elif self.get_option("secret_handler") == "base64":
                                secrets = get_base64_secrets(
                                    service_definition)
                            elif self.get_option("secret_handler") == "conjur":
                                secrets = get_conjur_secrets(
                                    service_definition,
                                    self.get_option("conjur_addr"),
                                    self.get_option("conjur_account"),
                                    self.get_option("conjur_token_path"),
                                    self.get_option("conjur_verify"))
                            for key, value in secrets.items():
                                self.inventory.set_variable(
                                    service, key, value)
        except Exception as e:
            raise AnsibleError(format(e))
"""

playbook_include_role = """
- hosts: "{{ pattern }}"
  gather_facts: no
  tasks:
    - include_role:
        name: "{{ ansible_role }}"
- hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - set_fact:
        output_dict: "{{ hostvars }}"
    - copy:
        content: "{{ output_dict | to_nice_json }}"
        dest: "{{ outputs_path | default('/tmp/outputs.json') }}"
"""


class AnsibleHandler(Handler):
    """Handler for functional requirements using the 'ansible' tool

    :param invoc: Invocation parameters received by grpc, the exact fields can be found at [stackl/agents/grpc_base/protos/agent_pb2.py](stackl/agents/grpc_base/protos/agent_pb2.py)
    :type invoc: Invocation instance with attributes
Example invoc:
class Invocation():
    def __init__(self):
        self.image = "tf_vm_vmw_win"
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
        if self._functional_requirement_obj.outputs:
            self._output = AnsibleOutput(self._functional_requirement_obj,
                                         self._invoc.stack_instance)
        self._env_list = {
            "ANSIBLE_INVENTORY_PLUGINS": "/opt/ansible/plugins/inventory",
            "ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED": "True"
        }
        if isinstance(self._secret_handler, VaultSecretHandler):
            stackl_inv = {
                "plugin": "stackl",
                "host": environ['STACKL_HOST'],
                "stack_instance": self._invoc.stack_instance,
                "vault_token_path": self._secret_handler._vault_token_path,
                "vault_addr": self._secret_handler._vault_addr,
                "secret_handler": "vault"
            }
        elif isinstance(self._secret_handler, Base64SecretHandler):
            stackl_inv = {
                "plugin": "stackl",
                "host": environ['STACKL_HOST'],
                "stack_instance": self._invoc.stack_instance,
                "secret_handler": "base64"
            }
        elif isinstance(self._secret_handler, ConjurSecretHandler):
            stackl_inv = {
                "plugin": "stackl",
                "host": environ['STACKL_HOST'],
                "stack_instance": self._invoc.stack_instance,
                "secret_handler": "conjur",
                "conjur_addr": self._secret_handler._conjur_appliance_url,
                "conjur_account": self._secret_handler._conjur_account,
                "conjur_token_path":
                self._secret_handler._conjur_authn_token_file,
                "conjur_verify": self._secret_handler._conjur_verify
            }
        else:
            stackl_inv = {
                "plugin": "stackl",
                "host": environ['STACKL_HOST'],
                "stack_instance": self._invoc.stack_instance,
                "secret_handler": "none"
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
                "stackl.yml": yaml.dump(stackl_inv)
            }
        }, {
            "name": "stackl-plugin",
            "type": "config_map",
            "mount_path": "/opt/ansible/plugins/inventory/stackl.py",
            "sub_path": "stackl.py",
            "data": {
                "stackl.py": stackl_plugin
            }
        }, {
            "name": "stackl-playbook",
            "type": "config_map",
            "mount_path": "/opt/ansible/playbooks/stackl/",
            "data": {
                "playbook-role.yml": playbook_include_role
            }
        }]
        # If any outputs are defined in the functional requirement set in base_handler

        self._init_containers = []
        self._command = ["/bin/sh", "-c"]
        self._command_args = [
            self._service, "-m", "include_role", "-v", "-i",
            "/opt/ansible/playbooks/inventory/stackl.yml", "-a",
            "name=" + self._functional_requirement
        ]

    @property
    def create_command_args(self) -> List[str]:
        """The command arguments used in a job to create something with Ansible

        :return: A list with strings containing shell commands
        :rtype: List[str]
        """
        self._command_args = [
            'echo "${USER_NAME:-runner}:x:$(id -u):$(id -g):${USER_NAME:-runner} user:${HOME}:/sbin/nologin" >> /etc/passwd'
        ]
        if "ansible_playbook_path" in self.provisioning_parameters:
            self._command_args[
                0] += f' && ansible-playbook {self.provisioning_parameters["ansible_playbook_path"]} -v -i /opt/ansible/playbooks/inventory/stackl.yml'
        elif self._output:
            pattern = self._service + "_" + str(self.index)
            self._command_args[
                0] += f' && ansible-playbook /opt/ansible/playbooks/stackl/playbook-role.yml -e ansible_role={self._functional_requirement} -i /opt/ansible/playbooks/inventory/stackl.yml -e pattern={pattern} '
            self._command_args[
                0] += f'-e outputs_path={self._output.output_file} '
        else:
            pattern = self._service + "_" + str(self.index)
            self._command_args[
                0] += f' && ansible {pattern} -m include_role -v -i /opt/ansible/playbooks/inventory/stackl.yml -a name={self._functional_requirement}'

        return self._command_args

    @property
    def delete_command_args(self) -> List[str]:
        """The command arguments used in a job to delete something with Ansible

        :return: A list with strings containing shell commands
        :rtype: List[str]
        """
        delete_command_args = self.create_command_args
        delete_command_args[0] += ' -e state=absent'
        return delete_command_args
