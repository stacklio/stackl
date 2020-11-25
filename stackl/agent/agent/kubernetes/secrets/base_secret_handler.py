"""
Module for the abstract SecretHandler class
"""
from abc import ABC

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
        self._env_list = {}
        self._init_containers = []

    @property
    def secrets(self):
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return service_definition.secrets

    @property
    def params(self):
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return service_definition.provisioning_parameters

    @property
    def init_containers(self):
        return self._init_containers

    @init_containers.setter
    def init_containers(self, value):
        self._init_containers = value

    @property
    def env_list(self):
        return self._env_list

    @env_list.setter
    def env_list(self, value):
        self._env_list = value

    @property
    def volumes(self):
        return self._volumes

    @volumes.setter
    def volumes(self, value):
        self._volumes = value
