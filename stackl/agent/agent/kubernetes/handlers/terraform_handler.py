"""
Module for Terraform automation through stackl
"""
import json
from typing import List

from jinja2 import Template

from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.outputs.terraform_output import TerraformOutput

from .base_handler import Handler


class TerraformHandler(Handler):
    """
    Handler for functional requirements using the 'terraform' tool
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
        if self._functional_requirement_obj.outputs:
            self._output = TerraformOutput(self._service,
                                           self._functional_requirement_obj,
                                           self._invoc.stack_instance,
                                           self._invoc.infrastructure_target)
        """
        Volumes is an array containing dicts that define Kubernetes volumes
        {
            name: affix for volume name, str
            type: 'config_map' or 'empty_dir', str
            data: dict with keys for files and values with strings, dict
            mount_path: the volume mount path in the automation container, str
            sub_path: a specific file in the volume, str
        }
        """
        self._volumes = [self.variables_volume_mount]
        self.terraform_backend_enabled = False
        if 'terraform_backend' in self.provisioning_parameters:
            self.terraform_backend_enabled = True
        if self.terraform_backend_enabled:
            backend_template = json.dumps(
                self.provisioning_parameters['terraform_backend'])
            parameters = {
                **self._invoc.__dict__,
                **self.provisioning_parameters
            }
            self._volumes.append({
                "name": "terraform-backend",
                "type": "config_map",
                "mount_path": "/tmp/backend",
                'data': {
                    'backend.tf.json':
                    Template(backend_template).render(parameters)
                }
            })
        self._env_list = {
            "TF_IN_AUTOMATION": "1",
            "KUBE_NAMESPACE": {
                "field_ref": 'metadata.namespace'
            }
        }
        self.variables_file = '/tmp/variables/variables.json'

    @property
    def variables_volume_mount(self):
        """
        Returns the config map definition used for the variables
        """
        return {
            "name": "variables",
            "type": "config_map",
            "mount_path": "/tmp/variables",
            "data": {
                "variables.json": json.dumps(self.provisioning_parameters)
            }
        }

    @property
    def create_command_args(self) -> List[str]:
        # Use /bin/sh because otherwise we can't chain multiple commands (with &&)
        command_args = ["/bin/sh", "-c"]
        terraform_commands = ""

        if self._secret_handler.terraform_backend_enabled or self.terraform_backend_enabled:
            terraform_commands += 'cp /tmp/backend/backend.tf.json /opt/terraform/plan/ && '

        terraform_commands += f'terraform init && terraform apply -auto-approve -var-file {self.variables_file}'

        if self._secret_handler.secret_variables_file:
            terraform_commands += f' -var-file {self._secret_handler.secret_variables_file}'

        terraform_commands = self._secret_handler.customize_commands(
            terraform_commands)

        if self._output:
            terraform_commands = self._output.customize_commands(
                terraform_commands)

        command_args.append(terraform_commands)
        return command_args

    @property
    def delete_command_args(self) -> list:
        """
        Constructs the delete command to destroy resources with terraform
        """
        # Use /bin/sh because otherwise we can't chain multiple commands (with &&)
        command_args = ["/bin/sh", "-c"]
        terraform_commands = ""

        if self._secret_handler.terraform_backend_enabled or self.terraform_backend_enabled:
            terraform_commands += 'cp /tmp/backend/backend.tf.json /opt/terraform/plan/ && '

        terraform_commands += f'terraform init && terraform destroy -auto-approve -var-file {self.variables_file}'

        if self._secret_handler.secret_variables_file:
            terraform_commands += f' -var-file {self._secret_handler.secret_variables_file}'

        terraform_commands = self._secret_handler.customize_commands(
            terraform_commands)

        command_args.append(terraform_commands)
        return command_args
