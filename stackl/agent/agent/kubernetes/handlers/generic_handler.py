"""
Module for any generic command through stackl
"""
from agent.kubernetes.kubernetes_secret_factory import get_secret_handler
from agent.kubernetes.secrets.vault_secret_handler import VaultSecretHandler
from .base_handler import Handler


class GenericHandler(Handler):
    """
    Handler for functional requirements using the 'generic' handler
    Example invoc:
    class Invocation():
        def __init__(self):
            self.image = "generic_example_image"
            self.infrastructure_target = "vsphere.brussels.vmw-vcenter-01"
            self.stack_instance = "instance-1"
            self.service = "generic_example"
            self.functional_requirement = "generic_example"
            self.tool = "generic"
            self.action = "create"
            self.command = "echo 'example'"
    """
    def __init__(self, invoc):
        super().__init__(invoc)
        self._secret_handler = get_secret_handler(invoc, self._stack_instance,
                                                  "env")
        self._create_command = self._invoc.create_command
        self._create_command_args = self._invoc.create_command_args
        self._delete_command = self._invoc.delete_command
        self._delete_command_args = self._invoc.delete_command_args

    @property
    def env_list(self) -> dict:
        env_list = {**self._env_list}
        if self.secret_handler:
            env_list.update(self.secret_handler.env_list)
        if self._output:
            env_list.update(self._output.env_list)
        env_list.update(self.provisioning_parameters)
        return env_list

    @property
    def command_args(self):
        command_args = ['']
        if isinstance(self._secret_handler, VaultSecretHandler):
            command_args[0] += (f"source {self._secret_handler.destination} && ")
        if self._invoc.action == "create" or self._invoc.action == "update":
            for args in self.create_command_args:
                command_args[0] += args
        if self._invoc.action == "delete":
            for args in self.delete_command_args:
                command_args[0] += args
        return command_args

    @property
    def create_command(self):
        return self._create_command

    @property
    def create_command_args(self):
        return self._create_command_args

    @property
    def delete_command(self):
        return self._create_command

    @property
    def delete_command_args(self):
        return self._delete_command_args

    @property
    def command(self):
        if self._invoc.action == "create" or self._invoc.action == "update":
            return self.create_command
        elif self._invoc.action == "delete":
            return self.delete_command
