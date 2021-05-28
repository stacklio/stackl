"""
Module for generic output logic
"""
from json import dumps
from typing import List

from kubernetes import client
from agent import config


class Output:
    # pylint: disable=too-many-instance-attributes
    """
    Superclass for outputs
    """
    def __init__(self, service, functional_requirement,
                 stackl_instance_name: str, infrastructure_target: str):
        self.output_file = ''
        self._command_args = ''
        self.stackl_host = config.settings.stackl_host
        self.stackl_cli_image = config.settings.stackl_cli_image
        self.stackl_cli_command = ['/bin/bash', '-c']
        self.service = service
        self.functional_requirement = functional_requirement
        self.infrastructure_target = infrastructure_target
        self.env_list = {}
        self.stackl_instance_name = stackl_instance_name
        self._spec_mount = {
            "name": "outputs-spec",
            "type": "config_map",
            "mount_path": "/mnt/stackl/spec",
            "data": {
                "spec.json": dumps(self.functional_requirement.outputs)
            }
        }
        self.volumes = [self._spec_mount]
        self.init_containers = []

    @property
    def stackl_cli_command_args(self):
        """
        Default command for the output container, can be overwritten by subclass
        """
        return f'\
            echo "Waiting for automation output to appear" &&\
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done;\
            cat {self.output_file} && \
            convert_json_from_spec --doc {self.output_file} --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            stackl connect {self.stackl_host} && \
            stackl update instance {self.stackl_instance_name} -p "$(cat {self.output_file})" -d'

    @property
    def stackl_container(self):
        """
        Returns the kubernetes container object for outputs
        """
        return client.V1Container(name='stackl-output',
                                  image=self.stackl_cli_image,
                                  env=self.env,
                                  volume_mounts=self.volume_mounts,
                                  image_pull_policy='Always',
                                  command=self.stackl_cli_command,
                                  args=[self.stackl_cli_command_args])

    @property
    def containers(self) -> List[client.V1Container]:
        """
        Get all containers used for outputs
        """
        containers = [self.stackl_container]
        return containers

    @property
    def command_args(self) -> str:
        """
        Returns the command ran in the output container
        """
        return self._command_args

    @property
    def spec_mount(self):
        """
        Returns the specifications of volume mounts
        """
        return self._spec_mount

    def customize_commands(self, current_command):
        """
        Customize commands to make outputs available to Stackl
        """
        return current_command
