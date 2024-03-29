"""
This module contains everything needed to handle outputs in Terraform
and save them in Stackl
"""
from .output import Output


class TerraformOutput(Output):
    """
    Class containing all logic to push outputs to Stackl
    """
    def __init__(self, service, functional_requirement,
                 stackl_instance_name: str, infrastructure_target: str):
        super().__init__(service, functional_requirement, stackl_instance_name,
                         infrastructure_target)
        self.output_file = '/mnt/terraform/output/result.json'

        self.env_list = {"TF_IN_AUTOMATION": "1"}
        self.volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/terraform/output"
        })

    @property
    def stackl_cli_command_args(self):
        """
        Returns the command that will run in the output container
        """
        return f'\
            echo "Waiting for automation output to appear" && \
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done; \
            ls -lh {self.output_file} && \
            ls -lh {self._spec_mount["mount_path"]} && \
            convert_json_from_spec --doc {self.output_file} \
            --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            export outputs="$(cat {self.output_file})" && \
            echo "outputs is $outputs" && \
            stackl connect {self.stackl_host} && \
            stackl update outputs {self.stackl_instance_name} -p "$outputs" -s {self.service} \
            -i {self.infrastructure_target} && \
            stackl get instance {self.stackl_instance_name} -o yaml '

    def customize_commands(self, current_command):
        """
        Customize commands to make outputs available to Stackl
        """
        return current_command + f' && terraform show -json > {self.output_file} \
                                && ls -lh {self.output_file}'