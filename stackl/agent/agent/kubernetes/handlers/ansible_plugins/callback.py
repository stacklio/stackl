ANSIBLE_CALLBACK_PLUGIN="""
DOCUMENTATION = '''
    author: @GBrawl
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


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'

    def __init__(self):
        super(CallbackModule, self).__init__()
        configuration = stackl_client.Configuration()
        configuration.host = self.get_option("stackl_url")

        api_client = stackl_client.ApiClient(configuration=configuration)
        self.fr_api = stackl_client.FunctionalRequirementsApi(
            api_client=api_client)
        self.outputs_api = stackl_client.OutputsApi(api_client=api_client)
        ###
        self.functional_requirement = self.get_option("functional_requirement")
        self.service = self.get_option("service")
        self.stack_instance = self.get_option("stack_instance")
        self.infrastructure_target = self.get_option("infrastructure_target")

    def v2_playbook_on_stats(self, stats):
        functional_requirement = self.fr_api.get_functional_requirement_by_name(
            self.functional_requirement)
        if "_run" in stats.custom:
            outputs = stats.custom["_run"]
        else:
            outputs = {}

        outputs_update = stackl_client.OutputsUpdate(
            outputs=outputs,
            infrastructure_target=self.infrastructure_target,
            service=self.service,
            stack_instance=self.stack_instance)
        self.outputs_api.add_outputs(outputs_update)
        self._display.display(str(stats.custom))
        self._display.display("Hallo callback module")
"""