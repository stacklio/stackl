import json
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
        return {"TF_IN_AUTOMATION": "1"}

    def get_variables_json(self):
        return json.dumps(
            self.stack_instance.services[self.service].provisioning_parameters)

    def get_volumes(self):
        volumes = []
        variables = {
            "name": "variables",
            "type": "config_map",
            "mount_path": "/tmp/variables",
            "data": {
                "variables.json": self.get_variables_json()
            }
        }

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
        volumes.append(variables)
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
        args[
            0] += " -var-file /tmp/secrets/secret.json -var-file /tmp/variables/variables.json --auto-approve"
        return args
