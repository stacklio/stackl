from json import dumps

from .base_handler import Handler
from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.outputs.packer_output import PackerOutput


class PackerHandler(Handler):
    def __init__(self, invoc):
        super().__init__(invoc)
        self._secret_handler = get_secret_handler(invoc, self._stack_instance,
                                                  "json")
        if self._functional_requirement_obj.outputs:
            self._output = PackerOutput(self._functional_requirement_obj,
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
        self._volumes = [{
            "name": "variables",
            "type": "config_map",
            "mount_path": "/tmp/variables",
            "data": {
                "variables.json": dumps(self.packer_variables())
            }
        }]
        if self._output:
            self._volumes.append(self._output.volume_mount)
            self._volumes.append(self._output.spec_mount)
        self._command = ["/bin/sh", "-c"]
        self._command_args = ["packer build -force"]
        self._command_args[0] \
            += " -var-file /tmp/secrets/secret.json -var-file /tmp/variables/variables.json"
        self._command_args[0] += " /opt/packer/packer.json"

    def packer_variables(self):
        d = {}
        for key, value in self._stack_instance.services[
                self._invoc.service].provisioning_parameters.items():
            d[key] = str(value)
        return d

    @property
    def create_command_args(self) -> list:
        command_args = [
            f'packer build -force -var-file /tmp/variables/variables.json'
        ]
        if self._secret_handler:
            command_args[0] += f' -var-file /tmp/secrets/secret.json'
        if self._output:
            command_args[0] += f'{self._output.command_args}'
        command_args[0] += ' /opt/packer/packer.json'
        return command_args

    @property
    def delete_command_args(self) -> list:
        return []
