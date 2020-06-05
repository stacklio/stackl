import base64
import json
import logging

import yaml
from stackl_client import StackInstance

from secrets.base_secret_handler import SecretHandler


class Base64SecretHandler(SecretHandler):
    def __init__(self, invoc, stack_instance: StackInstance,
                 secret_format: str):
        super().__init__(invoc, stack_instance, secret_format)
        self._destination = f"/tmp/secrets/secret.{self._secret_format}"
        self._volumes = [{
            "name": "secrets",
            "type": "config_map",
            "mount_path": "/tmp/secrets",
            "data": {
                f"secret.{self._secret_format}":
                self._provisioning_secrets(self._secret_format)
            }
        }]

    def _provisioning_secrets(self, format: str):
        secrets = self.secrets
        decoded_secrets = {}
        for key, secret in secrets.items():
            try:
                decoded_secrets[key] = base64.b64decode(secret +
                                                        "===").decode("utf-8")
            except Exception:
                logging.error("Could not decode secret")
        if format == "json":
            return json.dumps(decoded_secrets)
        elif format == "yaml":
            return yaml.dump(decoded_secrets)
