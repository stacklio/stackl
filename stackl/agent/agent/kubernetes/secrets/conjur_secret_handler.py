"""
Module containing all logic for retrieving secrets from Conjur
"""
import json
import os

from .base_secret_handler import SecretHandler


class ConjurSecretHandler(SecretHandler):
    # pylint: disable=too-many-instance-attributes
    # We just need a lot of fields for Conjur for the different options
    """
    Implementation of a SecretHandler using Conjur
    """
    def __init__(self, invoc, stack_instance, secret_format,
                 authenticator_client_container_name, conjur_appliance_url,
                 conjur_account, conjur_authn_token_file, conjur_authn_url,
                 conjur_authn_login, conjur_ssl_config_map,
                 conjur_ssl_config_map_key, conjur_verify):
        # pylint: disable=too-many-arguments
        # We just need more than 5 for conjur
        super().__init__(invoc, stack_instance, secret_format)
        self._invoc = invoc
        self._authenticator_client_container_name = authenticator_client_container_name
        self._conjur_appliance_url = conjur_appliance_url
        self._conjur_account = conjur_account
        self._conjur_authn_token_file = conjur_authn_token_file
        self._conjur_authn_url = conjur_authn_url
        self._conjur_authn_login = conjur_authn_login
        self._conjur_ssl_config_map = conjur_ssl_config_map
        self._conjur_ssl_config_map_key = conjur_ssl_config_map_key
        self._conjur_verify = conjur_verify
        self._volumes = [{
            "name": "conjur-access-token",
            "type": "empty_dir",
            "mount_path": "/run/conjur"
        }, {
            'name': 'conjur-secrets',
            'mount_path': '/tmp/conjur',
            'type': 'config_map',
            'data': {
                'secrets.yml': self._format_secrets_yaml()
            }
        }, {
            'name': 'terraform-backend',
            'mount_path': '/tmp/backend',
            'type': 'config_map',
            'data': {
                'backend.tf.json': json.dumps(self._format_template())
            }
        }]
        self._init_containers = [{
            "name": self._authenticator_client_container_name,
            "image": "cyberark/conjur-authn-k8s-client",
        }]
        self._env_list = {
            "CONTAINER_MODE": "init",
            "CONJUR_AUTHN_TOKEN_FILE": "/run/conjur/access-token",
            "CONJUR_APPLIANCE_URL": self._conjur_appliance_url,
            "CONJUR_AUTHN_URL": self._conjur_authn_url,
            "CONJUR_ACCOUNT": self._conjur_account,
            "CONJUR_AUTHN_LOGIN": self._conjur_authn_login,
            "MY_POD_NAME": {
                "field_ref": 'metadata.name'
            },
            "MY_POD_NAMESPACE": {
                "field_ref": 'metadata.namespace'
            },
            "MY_POD_IP": {
                "field_ref": 'status.podIP'
            },
            "CONJUR_SSL_CERTIFICATE": {
                "config_map_key_ref": {
                    "key": self._conjur_ssl_config_map_key,
                    "name": self._conjur_ssl_config_map
                }
            }
        }
        self.stackl_inv = {
            "plugin": "stackl",
            "host": os.environ['STACKL_HOST'],
            "stack_instance": self._invoc.stack_instance,
            "secret_handler": "conjur",
            "conjur_addr": self._conjur_appliance_url,
            "conjur_account": self._conjur_account,
            "conjur_token_path": self._conjur_authn_token_file,
            "conjur_verify": self._conjur_verify
        }

    def _format_secrets_yaml(self):
        yaml_string = ""
        for k, v in self.secrets.items():
            yaml_string += f"{k}: {v}\n"
        return yaml_string

    def _format_template(self):
        if "terraform_statefile_config" in self.secrets:
            self.terraform_backend_enabled = True
            return self.secrets['terraform_statefile_config']
        return None

    @staticmethod
    def add_extra_commands(current_command):
        """
        Adds extra commands used by conjur
        """
        return current_command.replace(
            "&&",
            "&& summon --provider summon-conjur -f /tmp/conjur/secrets.yml")
