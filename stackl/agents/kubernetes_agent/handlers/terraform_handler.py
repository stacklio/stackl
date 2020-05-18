import json
from handlers.base_handler import Handler
from outputs.terraform_output import TerraformOutput
from secret_factory import get_secret_handler


class TerraformHandler(Handler):
    """Handler for functional requirements using the 'terraform' tool

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
        self.tool = "terraform"
        self.action = "create"
"""
    def __init__(self, invoc):
        super().__init__(invoc)
        self._secret_handler = get_secret_handler(invoc, self._stack_instance,
                                                  "json")
        self._command = ["/bin/sh", "-c"]
        if self._functional_requirement_obj.outputs:
            self._output = TerraformOutput(self._functional_requirement_obj,
                                           self._invoc.stack_instance)
        """ Volumes is an array containing dicts that define Kubernetes volumes
        volume = {
            name: affix for volume name, str
            type: 'config_map' or 'empty_dir', str
            data: dict with keys for files and values with strings, dict
            mount_path: the volume mount path in the automation container, str
            sub_path: a specific file in the volume, str
        }
        """
        self._volumes = [self.variables_volume_mount]
        self._env_list = {"TF_IN_AUTOMATION": "1"}
        self.secret_variables_file = '/tmp/secrets/secret.json'
        self.variables_file = '/tmp/variables/variables.json'

    @property
    def variables_volume_mount(self):
        return {
            "name": "variables",
            "type": "config_map",
            "mount_path": "/tmp/variables",
            "data": {
                "variables.json": self.provisioning_parameters_json_string()
            }
        }

    @property
    def provisioning_parameters(self):
        return self._provisioning_parameters

    @provisioning_parameters.setter
    def provisioning_parameters(self, provisioning_parameters: dict):
        self._provisioning_parameters = provisioning_parameters

    def provisioning_parameters_json_string(self) -> str:
        """Returns provisioning_parameters which is a json dict to a flat string

        :return: provisioning_parameters
        :rtype: str
        """
        return json.dumps(self.provisioning_parameters)

    @property
    def command(self):
        return ["/bin/sh", "-c"]

    @property
    def create_command_args(self) -> list:
        command_args = []
        if self._secret_handler.terraform_backend_enabled:
            command_args.append(
                f'mv /tmp/backend/backend.tf.json /opt/terraform/plan/ && terraform init'
            )
        else:
            command_args.append(f'terraform init')
        if self._secret_handler and self._secret_handler.terraform_backend_enabled:
            command_args[
                0] += f' -backend-config=key={self._stack_instance.name}'
        command_args[
            0] += f' && terraform apply -auto-approve -var-file {self.variables_file}'

        if self._secret_handler:
            command_args[0] += f' -var-file {self.secret_variables_file}'
        if self._output:
            command_args[0] += f' {self._output.command_args}'
        return command_args

    @property
    def delete_command_args(self) -> list:
        command_args = []
        if self._secret_handler.terraform_backend_enabled:
            command_args.append(
                f'mv /tmp/backend/backend.tf.json /opt/terraform/plan/ && terraform init'
            )
        else:
            command_args.append(f'terraform init')
        if self._secret_handler and self._secret_handler.terraform_backend_enabled:
            command_args[
                0] += f' -backend-config=key={self._stack_instance.name}'
        command_args[
            0] += f' && terraform destroy -auto-approve -var-file {self.variables_file}'

        if self._secret_handler:
            command_args[0] += f' -var-file {self.secret_variables_file}'
        if self._output:
            command_args[0] += f' {self._output.command_args}'
        return command_args
