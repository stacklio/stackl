"""
Module for the abstract SecretHandler class
"""
from abc import ABC, abstractmethod

from stackl_client import StackInstance


class SecretHandler(ABC):
    """
    Abstract class which can be used as a helper when implementing a new secret handler
    """
    def __init__(self, invoc, stack_instance: StackInstance,
                 secret_format: str):
        self.terraform_backend_enabled = False
        self._invoc = invoc
        self._secret_format = secret_format.lower()
        self._stack_instance = stack_instance
        self._service = self._invoc.service
        self.secret_variables_file = None
        self.env_list = {}
        self.init_containers = []
        self.volumes = []

    @property
    def secrets(self):
        """
        Get all secrets
        """
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return service_definition.secrets
        return None

    def customize_commands(self, current_command):
        """
        Customize commands used by the secret handler, by default just return commands
        """
        return current_command
