import os

import click
import stackl_client


class StacklContext(object):
    def __init__(self):
        with open(config_path, 'r+') as stackl_config:
            host = stackl_config.read()
        configuration = stackl_client.Configuration()
        configuration.host = host
        self.api_client = stackl_client.ApiClient(configuration=configuration)
        self.documents_api = stackl_client.DocumentsApi(
            api_client=self.api_client)
        self.functional_requirements_api = stackl_client.FunctionalRequirementsApi(
            api_client=self.api_client)
        self.services_api = stackl_client.ServicesApi(
            api_client=self.api_client)
        self.sat_api = stackl_client.StackApplicationTemplatesApi(
            api_client=self.api_client)
        self.sit_api = stackl_client.StackInfrastructureTemplatesApi(
            api_client=self.api_client)
        self.stack_instances_api = stackl_client.StackInstancesApi(
            api_client=self.api_client)
        self.policies_api = stackl_client.PoliciesApi(
            api_client=self.api_client)


pass_stackl_context = click.make_pass_decorator(StacklContext, ensure=True)

config_path = os.path.expanduser('~') + os.sep + '.stackl' + os.sep + 'config'
