from .output import Output


class TerraformOutput(Output):
    def __init__(self, functional_requirement, stackl_instance_name: str,
                 infrastructure_target: str):
        self.infrastructure_target = infrastructure_target
        super().__init__(functional_requirement, stackl_instance_name)
        self.output_file = '/mnt/terraform/output/result.json'
        self._command_args = f'&& terraform show -json > {self.output_file} && ls -lh {self.output_file}'

        self._env_list = {"TF_IN_AUTOMATION": "1"}
        self._volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/terraform/output"
        })

    @property
    def stackl_cli_command_args(self):
        return f'\
            echo "Waiting for automation output to appear" &&\
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done;\
            ls -lh {self.output_file} && \
            ls -lh {self._spec_mount["mount_path"]} && \
            convert_json_from_spec --doc {self.output_file} --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            export outputs="$(cat {self.output_file})" && \
            echo "outputs is $outputs" && \
            stackl connect {self.stackl_host} && \
            stackl update instance {self.stackl_instance_name} -p "$outputs" -p \'{{\"infrastructure_target\": \"{self.infrastructure_target}\"}}\' -d && \
            stackl get instance {self.stackl_instance_name} -o yaml '
