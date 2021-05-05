import os
from pathlib import Path

import click
import stackl_client.apis as stackl_apis
import stackl_client

class StacklContext(object):
    def __init__(self):
        try:
            with open(get_config_path(), 'r+') as stackl_config:
                host = stackl_config.read()
                configuration = stackl_client.Configuration()
                configuration.host = host
                self.api_client = stackl_client.ApiClient(configuration=configuration)
                self.infrastructure_base_api = stackl_apis.InfrastructureBaseApi(
                    api_client=self.api_client)
                self.functional_requirements_api = stackl_apis.FunctionalRequirementsApi(
                    api_client=self.api_client)
                self.services_api = stackl_apis.ServicesApi(
                    api_client=self.api_client)
                self.sat_api = stackl_apis.StackApplicationTemplatesApi(
                    api_client=self.api_client)
                self.sit_api = stackl_apis.StackInfrastructureTemplatesApi(
                    api_client=self.api_client)
                self.stack_instances_api = stackl_apis.StackInstancesApi(
                    api_client=self.api_client)
                self.policy_templates_api = stackl_apis.PolicyTemplatesApi(
                    api_client=self.api_client)
                self.snapshot_api = stackl_apis.SnapshotsApi(
                    api_client=self.api_client)
                self.outputs_api = stackl_apis.OutputsApi(api_client=self.api_client)
        except FileNotFoundError:
            click.echo(
                "Config file not found, run `stackl connect` first")
            exit(1)


pass_stackl_context = click.make_pass_decorator(StacklContext, ensure=False)


def get_config_path():
    if len(str(Path.home())) == 0:
        config_path = os.getcwd() + os.sep + '.stackl' + os.sep + 'config'
    else:
        config_path = str(Path.home()) + os.sep + '.stackl' + os.sep + 'config'
    return config_path
