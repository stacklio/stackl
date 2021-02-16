"""
Module for any generic command through stackl
"""
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
        self._create_command = self._invoc.create_command
        self._create_command_args = self._invoc.create_command_args
        self._delete_command = self._invoc.delete_command
        self._delete_command_args = self._invoc.delete_command_args

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
