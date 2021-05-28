"""
Module for Packer automation through stackl
"""
from json import dumps

from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.outputs.packer_output import PackerOutput
from .base_handler import Handler
from ..secrets.conjur_secret_handler import ConjurSecretHandler


class PackerHandler(Handler):
    """
    Class used for preparing everything for starting packer
    """
    def __init__(self, invoc):
        super().__init__(invoc)
        self._secret_handler = get_secret_handler(invoc, self._stack_instance,
                                                  "json")
        if self._functional_requirement_obj.outputs:
            self._output = PackerOutput(self._service,
                                        self._functional_requirement_obj,
                                        self._invoc.stack_instance,
                                        self._invoc.infrastructure_target)
        """
        Volumes is an array containing dicts that define Kubernetes volumes
        {
            name: affix for volume name, str
            type: config_map or empty_dir, str
            data: dict with keys for files and values with strings, dict
            mount_path: the volume mount path in the automation container, str
            sub_path: a specific file in the volume, str
        }
        """
        self._volumes = [{
            "name": "variables",
            "type": "config_map",
            "mount_path": "/tmp/variables",
            "data": {
                "variables.json": dumps(self.packer_variables())
            }
        }]
        if self._output:
            self._volumes.append(self._output.spec_mount)
        self._command = ["/bin/sh", "-c"]

    def packer_variables(self):
        """
        this method converts all values to string, because packer can't
        handle other types
        """
        d = {}
        pp = {}
        for si_service in self._stack_instance.services[self._invoc.service]:
            if si_service.infrastructure_target == self._invoc.infrastructure_target:
                pp = si_service.provisioning_parameters
        for key, value in pp.items():
            d[key] = str(value)
        return d

    @property
    def create_command_args(self) -> list:
        """
        This method returns the command args needed to run packer including
        all variables and secrets and optionally outputs
        """
        command_args = [""]
        if self._invoc.before_command is not None:
            command_args[0] += f"{self._invoc.before_command}  && "

        command_args[
            0] += "packer build -force -var-file /tmp/variables/variables.json"

        if self._secret_handler and not isinstance(self._secret_handler, ConjurSecretHandler):
            command_args[0] += ' -var-file /tmp/secrets/secret.json'
        if self._secret_handler:
            command_args[0] = self._secret_handler.add_extra_commands(command_args[0])
        if self._output:
            command_args[0] += f'{self._output.command_args}'
        command_args[0] += ' /opt/packer/src/packer.json'
        return command_args

    @property
    def delete_command_args(self) -> list:
        """
        Packer doesn't support deleting, so this is just a stub
        """
        return []
