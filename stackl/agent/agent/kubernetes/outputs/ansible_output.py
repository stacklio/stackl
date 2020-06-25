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
