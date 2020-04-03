from json import dumps

from handlers.base_handler import Handler
from handlers.vault_secret_handler import VaultSecretHandler


class TerraformHandler(Handler):
    def __init__(self):
        super().__init__()
        self.secret_handler = VaultSecretHandler("json")

    def parse_secrets(self):
        return dumps(self.secrets)

    def get_env_list(self):
        return {}

    def get_volumes(self):
        volumes = []
        # if self.invocation.stack_instance.services.secrets:
        # secret_volume = {
        #     "name": "secrets",
        #     "mount_path": "/opt/terraform/plan/secrets.tf",
        #     "sub_path": "secrets.tf",
        #     "type": "emptydir",
        #     "data": self.parse_secrets()
        # }
        # volumes.append(secret_volume)

        secrets = {
            "name": "secrets",
            "type": "empty_dir",
            "mount_path": "/tmp/secrets"
        }

        backend_config = {
            "name": "backend-config",
            "mount_path": "/opt/terraform/plan/backend.tf",
            "sub_path": "backend.tf",
            "type": "config_map",
            "data": {
                "backend.tf":
                """terraform {
  backend "s3" {
    bucket = "dome-nexus"
    access_key    = ""
    secret_key    = ""
    region = "eu-west-1"
  }
}"""
            }
        }
        volumes.append(backend_config)
        volumes.append(secrets)
        return volumes

    def get_command(self):
        return ["/bin/sh", "-c"]

    def get_command_args(self, action):
        args = ["terraform init"]
        if action == "create" or action == "update":
            args[0] += " && terraform apply"
        else:
            args[0] += " && terraform destroy"
        args[0] += " -var-file /tmp/secrets/secret.json"
        return args
