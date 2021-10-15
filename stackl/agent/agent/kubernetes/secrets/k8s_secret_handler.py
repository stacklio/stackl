"""
Module for Base64 Secret Handler
"""
import base64
import json
import logging
import os

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from stackl_client import StackInstance

from agent import config as agent_config
from agent.kubernetes.secrets.base_secret_handler import SecretHandler


class K8sSecretHandler(SecretHandler):
    """
    Implementation of the secrethandler using Base64 encoding
    """
    def __init__(self, invoc, stack_instance: StackInstance,
                 secret_format: str):
        super().__init__(invoc, stack_instance, secret_format)
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self._configuration = client.Configuration()
        self._api_instance_core = client.CoreV1Api(
            client.ApiClient(self._configuration))
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
            "secret_handler": "kubernetes"
        }

    def _provisioning_secrets(self, secret_format: str):
        secrets = self.secrets
        k8s_secrets = {}
        for _, secret in secrets.items():
            try:
                api_response = self._api_instance_core.read_namespaced_secret(
                    secret, agent_config.settings.stackl_namespace)
                logging.info(f"api_response: {api_response}")
                for k, v in api_response.data.items():
                    k8s_secrets[k] = base64.b64decode(v +
                                                      "===").decode("utf-8")
            except ApiException as e:
                logging.error(f"k8s secret error: {e}")
        if secret_format == "json":
            return json.dumps(k8s_secrets)
        if secret_format == "yaml":
            return yaml.dump(k8s_secrets)
        raise TypeError("secret format not supported")
