"""
This module handles returning outputs in Ansible from the agent to Stackl
"""
from .output import Output


class AnsibleOutput(Output):
    """
    Class handling all logic for returning outputs in ansible back to a stack instance
    """
    def __init__(self, service, functional_requirement, stackl_instance_name,
                 infrastructure_target, hostname):
        super().__init__(service, functional_requirement, stackl_instance_name,
                         infrastructure_target)
        self.output_file = '/mnt/ansible/output/result.json'
        self.hostname = hostname
        self._command_args = ''
        self._volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/ansible/output/"
        })

    @property
    def stackl_cli_command_args(self):
        """
        This function returns the command that has to be run in the outputs container
        for updating outputs in stackl
        """
        return f'\
            echo "Waiting for automation output to appear" &&\
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done;\
            cat {self.output_file} && \
            convert_json_from_spec -f {self.functional_requirement.outputs_format} --doc {self.output_file} \
            --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            stackl connect {self.stackl_host} && \
            stackl update outputs {self.stackl_instance_name} -p "$(cat {self.output_file})" \
            -s {self.service} -i {self.infrastructure_target}'
