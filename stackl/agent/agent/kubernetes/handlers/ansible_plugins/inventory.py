
STACKL_PLUGIN = """
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
import logging
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.module_utils._text import to_native
from ansible.module_utils._text import to_text
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


def create_groups(hosts, stackl_inventory_groups, infrastructure_target):
    groups = defaultdict(list)
    for item in stackl_inventory_groups:
        for tag in item["tags"]:
            for index in range(item["count"]):
                try:
                    host = {
                        "host": hosts[index],
                        "target": infrastructure_target
                    }
                except IndexError as e:
                    print(e)
                    exit(1)
                groups[tag].append(host)
        del hosts[0:item["count"]]
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

    def verify_stackl_client(self):
        r = requests.get(f'{self.get_option("host")}/openapi.json')
        stackl_version = r.json()['info']['version']
        stackl_client_version = stackl_client.__version__
        if stackl_client_version != stackl_version:
            logging.warn(
                "stackl-client version is not equal to Stackl version. This may cause issues."
            )

    def parse(self, inventory, loader, path, cache):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            self.verify_stackl_client()
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
                    if hasattr(
                            service_definition, "hosts"
                    ) and 'stackl_inventory_groups' in service_definition.provisioning_parameters:
                        if not check_groups(
                                stack_instance.groups,
                                service_definition.provisioning_parameters[
                                    'stackl_inventory_groups'],
                                service_definition.hosts):
                            stack_instance.groups = create_groups(
                                service_definition.hosts,
                                service_definition.provisioning_parameters[
                                    'stackl_inventory_groups'],
                                service_definition.infrastructure_target)
                            stack_update = stackl_client.StackInstanceUpdate(
                                stack_instance_name=stack_instance.name,
                                params={
                                    "stackl_groups": stack_instance.groups
                                },
                                disable_invocation=True)
                            api_instance.put_stack_instance(stack_update)
                            stack_instance = api_instance.get_stack_instance(
                                stack_instance_name)
                        for item, value in stack_instance.groups.items():
                            self.inventory.add_group(item)
                            for group in value:
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
                                    elif self.get_option(
                                            "secret_handler") == "conjur":
                                        secrets = get_conjur_secrets(
                                            service_definition,
                                            self.get_option("conjur_addr"),
                                            self.get_option("conjur_account"),
                                            self.get_option(
                                                "conjur_token_path"),
                                            self.get_option("conjur_verify"))
                                    for key, value in secrets.items():
                                        self.inventory.set_variable(
                                            item, key, value)
                    else:
                        self.inventory.add_group(service)
                        if service_definition.hosts:
                            for h in service_definition.hosts:
                                self.inventory.add_host(host=h, group=service)
                        else:
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
            raise AnsibleError('Error: this was original exception: %s' %
                               to_native(e))
"""