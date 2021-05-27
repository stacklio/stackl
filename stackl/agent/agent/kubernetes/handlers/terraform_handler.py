"""
Module for Terraform automation through stackl
"""
import json
from jinja2 import Template

from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.outputs.terraform_output import TerraformOutput

from ..secrets.conjur_secret_handler import ConjurSecretHandler
from ..secrets.vault_secret_handler import VaultSecretHandler
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
        self._command = ["/bin/sh", "-c"]
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
        self.secret_variables_file = '/tmp/secrets/secret.json'
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
                "variables.json": self.provisioning_parameters_json_string()
            }
        }

    def provisioning_parameters_json_string(self) -> str:
        """Returns provisioning_parameters which is a json dict to a flat string

        :return: provisioning_parameters
        :rtype: str
        """
        return json.dumps(self.provisioning_parameters)

    @property
    def command(self):
        return self._command

    @property
    def create_command_args(self) -> list:
        command_args = super().create_command_args
        if self._secret_handler.terraform_backend_enabled or self.terraform_backend_enabled:
            command_args[
                0] += 'cp /tmp/backend/backend.tf.json /opt/terraform/plan/ && terraform init'
        else:
            command_args[0] += 'terraform init'
        # if self._secret_handler and self._secret_handler.terraform_backend_enabled:
        #     command_args[
        #         0] += f' -backend-config=key={self._stack_instance.name}'
        command_args[
            0] += f' && terraform apply -auto-approve -var-file {self.variables_file}'

        if self._secret_handler and not isinstance(self._secret_handler,
                                                   ConjurSecretHandler):
            command_args[0] += f' -var-file {self.secret_variables_file}'
        if self._secret_handler:
            command_args[0] = self._secret_handler.add_extra_commands(
                command_args[0])
        if self._output:
            command_args[0] += f' {self._output.command_args}'
        return command_args

    @property
    def delete_command_args(self) -> list:
        """
        Constructs the delete command to destroy resources with terraform
        """
        command_args = []
        if self._secret_handler.terraform_backend_enabled or self.terraform_backend_enabled:
            command_args.append(
                'cp /tmp/backend/backend.tf.json /opt/terraform/plan/ && terraform init'
            )
        else:
            command_args.append('terraform init')

        command_args[
            0] += f' && terraform destroy -auto-approve -var-file {self.variables_file}'

        if self._secret_handler and not isinstance(self._secret_handler,
                                                   ConjurSecretHandler):
            command_args[0] += f' -var-file {self.secret_variables_file}'
        elif isinstance(self._secret_handler, ConjurSecretHandler):
            command_args[0] = ConjurSecretHandler.add_extra_commands(
                command_args[0])
        if self._output:
            command_args[0] += f' {self._output.command_args}'
        return command_args
