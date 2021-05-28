"""
Module containing all logic for retrieving secrets from Hashicorp Vault
"""

import os
from jinja2 import Template
from .base_secret_handler import SecretHandler

VAULT_AGENT_CONFIG = """
exit_after_auth = false
pid_file = "%s"
auto_auth {
    method "kubernetes" {
        mount_path = "%s"
        config = {
            role = "%s"
        }
    }
    sink "file" {
        config = {
            path = "%s"
            mode = 0755
        }
    }
}

template {
  destination = "%s"
  error_on_missing_key = true
  contents = <<EOH
%s
EOH
}
"""

EXTRA_TEMPLATE = """

template {
  destination = "%s"
  contents = <<EOH
%s
EOH
}
"""

ENVCONSUL_CONFIG = """
vault {
    vault_agent_token_file = "{{ vault_token_path }}"
}
{% for secret_path in secret_paths %}
secret {
    no_prefix = true,
    path = "{{ secret_path }}"
}
{% endfor %}
"""


class VaultSecretHandler(SecretHandler):
    # pylint: disable=too-many-instance-attributes
    # We just need a lot of fields for vault
    """
    Implementation of a secrethandler using Hashicorp Vault
    """
    def __init__(self, invoc, stack_instance, vault_addr: str,
                 secret_format: str, vault_role: str, vault_mount_point: str,
                 vault_image: str):
        # pylint: disable=too-many-arguments
        # We just need more than 5 for vault
        super().__init__(invoc, stack_instance, secret_format)
        self._vault_role = vault_role
        self._vault_addr = vault_addr
        self._vault_mount_point = vault_mount_point
        self.terraform_backend_enabled = False
        self._invoc = invoc
        self._secret_format = secret_format.lower()
        self._pid_file = "/home/vault/pidfile"
        self._vault_token_path = "/tmp/vault/.vault-token"
        self._stack_instance = stack_instance
        self.secret_variables_file = f"/tmp/secrets/secret.{self._secret_format}"
        self.volumes = [{
            'name': 'vault-agent-config',
            'mount_path': '/etc/vault-config',
            'type': 'config_map',
            'data': {
                'vault-agent-config.hcl': self._format_template()
            }
        }, {
            'name': 'envconsul-config',
            'mount_path': '/etc/envconsul-config',
            'type': 'config_map',
            'data': {
                'envconsul-config.hcl': self._format_envconsul_config()
            }
        }, {
            "name": "secrets",
            "type": "empty_dir",
            "mount_path": "/tmp/secrets"
        }, {
            "name": "vault-token",
            "type": "empty_dir",
            "mount_path": "/tmp/vault"
        }]
        if self.terraform_backend_enabled:
            self.volumes.append({
                "name": "terraform-backend-secrets",
                "type": "empty_dir",
                "mount_path": "/tmp/backend"
            })
        self.init_containers = [{
            "name":
            "vault-agent",
            "image":
            vault_image,
            "args": [
                "agent", "-config=/etc/vault-config/vault-agent-config.hcl",
                "-exit-after-auth"
            ]
        }]
        self.env_list = {"VAULT_ADDR": self._vault_addr}
        self.stackl_inv = {
            "plugin": "stackl",
            "host": os.environ['STACKL_HOST'],
            "stack_instance": self._invoc.stack_instance,
            "vault_token_path": self._vault_token_path,
            "vault_addr": self._vault_addr,
            "secret_handler": "vault"
        }

    def _format_envconsul_config(self):
        return Template(ENVCONSUL_CONFIG).render(
            vault_token_path=self._vault_token_path,
            secret_paths=self.secrets.values())

    def _format_template(self):
        content_string = ""
        if "backend_secret_path" in self.secrets:
            self.terraform_backend_enabled = True
            backend_secret_path = self.secrets['backend_secret_path']
        for _, (_, value) in enumerate(self.secrets.items()):
            content_string += """{{ with secret "%s" }}{{ range $key, $value := .Data.data }}
            {{ scratch.MapSet "secrets" $key $value }}{{ end }}{{ end }}""" % value
        if self._secret_format == "json":
            content_string += '{{ scratch.Get "secrets" | toJSON }}'
        elif self._secret_format == "yaml":
            content_string += '{{ scratch.Get "secrets" | toYAML }}'
        elif self._secret_format == "toml":
            content_string += '{{ scratch.Get "secrets" | toTOML }}'
        va_config = VAULT_AGENT_CONFIG % (
            self._pid_file, self._vault_mount_point, self._vault_role,
            self._vault_token_path, self.secret_variables_file, content_string)
        if self.terraform_backend_enabled:
            content_string = """{{ with secret "%s" }}{{ .Data.data | toJSON }}{{ end }}""" \
                                % backend_secret_path
            va_config += EXTRA_TEMPLATE % ("/tmp/backend/backend.tf.json",
                                           content_string)
        return va_config

    def customize_commands(self, current_command):
        """
        Customize commands to make secrets
        accessible as environment variables
        """
        return current_command.replace(
            "&&",
            "&& envconsul -config=/etc/envconsul-config/envconsul-config.hcl")