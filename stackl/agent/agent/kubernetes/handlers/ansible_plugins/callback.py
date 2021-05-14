"""
Stackl callback plugin for Ansible
"""
ANSIBLE_CALLBACK_PLUGIN = """
DOCUMENTATION = '''
    author: GBrawl
    name: stackl
    type: notification
    requirements:
      - stackl_client (pip install stackl-client)
    short_description: Sends stats back to Stackl
    description:
        - This plugin returns outputs to Stackl
    options:
      stackl_url:
        required: True
        type: string
        description: Stackl api url
        env:
          - name: STACKL_URL
        ini:
          - section: callback_stackl
            key: url
      stack_instance:
        required: True
        description: Stackl stack instance
        env:
          - name: STACKL_STACK_INSTANCE
        ini:
          - section: callback_stackl
            key: stack_instance
      service:
        required: True
        description: Stackl service
        env:
          - name: STACKL_SERVICE
        ini:
          - section: callback_stackl
            key: service
      functional_requirement:
        required: True
        description: Stackl functional_requirement
        env:
          - name: STACKL_FUNCTIONAL_REQUIREMENT
        ini:
          - section: callback_stackl
            key: functional_requirement
      infrastructure_target:
        required: True
        description: Stackl infrastructure target
        env:
          - name: STACKL_INFRASTRUCTURE_TARGET
        ini:
          - section: callback_stackl
            key: infrastructure_target
'''

from ansible.plugins.callback import CallbackBase
import stackl_client
from stackl_client import models

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'stackl'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()


    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        self.stackl_url = self.get_option('stackl_url')
        self.functional_requirement = self.get_option("functional_requirement")
        self.service = self.get_option("service")
        self.stack_instance = self.get_option("stack_instance")
        self.infrastructure_target = self.get_option("infrastructure_target")


    def v2_playbook_on_stats(self, stats):
        configuration = stackl_client.Configuration()
        configuration.host = self.stackl_url
        api_client = stackl_client.ApiClient(configuration=configuration)
        self.fr_api = stackl_client.apis.FunctionalRequirementsApi(
            api_client=api_client)
        self.outputs_api = stackl_client.apis.OutputsApi(api_client=api_client)
        functional_requirement = self.fr_api.get_functional_requirement_by_name(
            self.functional_requirement)
        if "_run" in stats.custom:
            outputs = stats.custom["_run"]
        else:
            outputs = stats.custom

        outputs_update = models.OutputsUpdate(
            outputs=outputs,
            infrastructure_target=self.infrastructure_target,
            service=self.service,
            stack_instance=self.stack_instance)
        self.outputs_api.add_outputs(outputs_update)
        self._display.display(str(stats.custom))
"""
