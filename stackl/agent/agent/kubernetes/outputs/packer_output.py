from .output import Output


class PackerOutput(Output):
    def __init__(self, functional_requirement, stackl_instance_name: str):
        super().__init__(functional_requirement, stackl_instance_name)

        self.output_file = '/mnt/packer/output/result.json'
        self._command_args = ' -var manifest_path={}'.format(self.output_file)
        self._volumes.append({
            "name": "outputs",
            "type": "empty_dir",
            "mount_path": "/mnt/packer/output/"
        })
        self.secret_variables_file = '/tmp/secrets/secret.json'
        self.variables_file = '/tmp/variables/variables.json'

    @property
    def command_args(self) -> str:
        return self._command_args
