"""
This module handles returning outputs in packer from the agent to Stackl
"""
from .output import Output


class PackerOutput(Output):
    """
    Class for handling outputs in Packer
    """
    def __init__(self, service, functional_requirement,
                 stackl_instance_name: str, infrastructure_target: str):
        super().__init__(service, functional_requirement, stackl_instance_name,
                         infrastructure_target)

        self.output_file = '/mnt/packer/output/result.json'
        self.volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/packer/output/"
        })
        self.secret_variables_file = '/tmp/secrets/secret.json'
        self.variables_file = '/tmp/variables/variables.json'

    def customize_commands(self, current_command):
        """
        Customize commands to make outputs available to Stackl
        """
        return current_command + f' -var manifest_path={self.output_file}'
