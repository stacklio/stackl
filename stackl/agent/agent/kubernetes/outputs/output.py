import os
from abc import abstractmethod
from kubernetes import client
from typing import List
from json import dumps


class Output:
    def __init__(self, functional_requirement, stackl_instance_name: str):
        self.stack_instance = None
        self.output_file = ''
        self.stackl_host = f'http://{os.environ["STACKL_HOST"]}'
        self.stackl_cli_image = 'stacklio/stackl-cli:v0.2.1'
        self.stackl_cli_command = ['/bin/bash', '-c']
        self._functional_requirement = functional_requirement
        self._env_list = {}
        self.stackl_instance_name = stackl_instance_name
        self._spec_mount = {
            "name": "outputs-spec",
            "type": "config_map",
            "mount_path": "/mnt/stackl/spec",
            "data": {
                "spec.json": dumps(self._functional_requirement.outputs)
            }
        }
        self._volumes = [self._spec_mount]
        self.init_containers = []

    @property
    def stackl_cli_command_args(self):
        return f'\
            echo "Waiting for automation output to appear" &&\
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done;\
            cat {self.output_file} && \
            convert_json_from_spec --doc {self.output_file} --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            stackl connect {self.stackl_host} && \
            stackl update instance {self.stackl_instance_name} -p "$(cat {self.output_file})" -d'

    @property
    def stackl_container(self):
        return client.V1Container(name='stackl-output',
                                  image=self.stackl_cli_image,
                                  env=self.env,
                                  volume_mounts=self.volume_mounts,
                                  image_pull_policy='Always',
                                  command=self.stackl_cli_command,
                                  args=[self.stackl_cli_command_args])

    @property
    @abstractmethod
    def containers(self) -> List[client.V1Container]:
        containers = [self.stackl_container]
        return containers

    @property
    def command_args(self) -> str:
        return self._command_args

    @property
    def spec_mount(self):
        return self._spec_mount

    @property
    def env_list(self):
        return self._env_list

    @property
    def volumes(self):
        return self._volumes
