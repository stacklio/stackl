from .output import Output


class AnsibleOutput(Output):
    def __init__(self, functional_requirement, stackl_instance_name):
        super().__init__(functional_requirement, stackl_instance_name)
        self.output_file = '/mnt/ansible/output/result.json'
        self._command_args = ''
        self._volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/ansible/output/"
        })


    @property
    def stackl_cli_command_args(self):
        return f'\
            echo "Waiting for automation output to appear" &&\
            while [[ ! -s "{self.output_file}" ]]; do sleep 2; done;\
            cat {self.output_file} && \
            convert_json_from_spec -f {self._functional_requirement.outputs_format} --doc {self.output_file} --spec {self._spec_mount["mount_path"]}/spec.json --output {self.output_file} && \
            stackl connect {self.stackl_host} && \
            stackl update instance {self.stackl_instance_name} -p "$(cat {self.output_file})" -d'