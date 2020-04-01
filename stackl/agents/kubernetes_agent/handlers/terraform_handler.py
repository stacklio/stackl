from stackl.application.handler import Handler
from json import dumps


class TerraformHandler(Handler):

    def parse_secrets(self):
        return dumps(self.secrets)

    def get_env_list(self):
        return {}

    def get_volumes(self):
        volumes = []
        if self.invocation.stack_instance.services.secrets:
            secret_volume = {
                "name": "secrets",
                "mount_path": "/opt/terraform/plan/secrets.tf",
                "sub_path": "secrets.tf",
                "type": "config_map",
                "data": self.parse_secrets()
            }
            volumes.append(secret_volume)

        backend_config = {
            "name": "backend-config",
            "mount_path": "/opt/terraform/plan/backend.tf",
            "sub_path": "backend.tf",
            "type": "config_map",
            "data": self.invocation.stack_instance.services
        }
        volumes.append(backend_config)
        return volumes

    def get_command(self):
        return ["/bin/sh", "-c"]

    def get_args(self):
        args = ["terraform init"]
        if self.action == "create" or self.action == "update":
            args.append(" && terraform apply")
        else:
            args.append(" && terraform destroy")
        args.append(" -var-file secrets.tf")
        return args

