"""
Module for Base64 Secret Handler
"""
import base64
import json
import logging
import os

import yaml
from stackl_client import StackInstance

from agent.kubernetes.secrets.base_secret_handler import SecretHandler


class Base64SecretHandler(SecretHandler):
    """
    Implementation of the secrethandler using Base64 encoding
    """
    def __init__(self, invoc, stack_instance: StackInstance,
                 secret_format: str):
        super().__init__(invoc, stack_instance, secret_format)
        self.secret_variables_file = f"/tmp/secrets/secret.{self._secret_format}"
        self.volumes = [{
            "name": "secrets",
            "type": "config_map",
            "mount_path": "/tmp/secrets",
            "data": {
                f"secret.{self._secret_format}":
                self._provisioning_secrets(self._secret_format)
            }
        }]
        self.stackl_inv = {
            "plugin": "stackl",
            "host": os.environ['STACKL_HOST'],
            "stack_instance": self._invoc.stack_instance,
            "secret_handler": "base64"
        }

    def _provisioning_secrets(self, secret_format: str):
        secrets = self.secrets
        decoded_secrets = {}
        for key, secret in secrets.items():
            try:
                decoded_secrets[key] = base64.b64decode(secret +
                                                        "===").decode("utf-8")
            except TypeError:
                logging.error(f"Base64 decode error")
        if secret_format == "json":
            return json.dumps(decoded_secrets)
        if secret_format == "yaml":
            return yaml.dump(decoded_secrets)
        raise TypeError("secret format not supported")
