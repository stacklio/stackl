"""
Module containing all logic for retrieving secrets from Hashicorp Vault
"""

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


class VaultSecretHandler(SecretHandler):
    """
    Implementation of a secrethandler using Hashicorp Vault
    """
    def __init__(self, invoc, stack_instance, vault_addr: str,
                 secret_format: str, vault_role: str, vault_mount_point: str):
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
        self._destination = f"/tmp/secrets/secret.{self._secret_format}"
        self._volumes = [{
            'name': 'vault-agent-config',
            'mount_path': '/etc/vault-config',
            'type': 'config_map',
            'data': {
                'vault-agent-config.hcl': self._format_template()
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
            self._volumes.append({
                "name": "terraform-backend-secrets",
                "type": "empty_dir",
                "mount_path": "/tmp/backend"
            })
        self._init_containers = [{
            "name":
            "vault-agent",
            "image":
            "vault:latest",
            "args": [
                "agent", "-config=/etc/vault-config/vault-agent-config.hcl",
                "-exit-after-auth"
            ]
        }]
        self._env_list = {"VAULT_ADDR": self._vault_addr}

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
            self._vault_token_path, self._destination, content_string)
        if self.terraform_backend_enabled:
            content_string = """{{ with secret "%s" }}{{ .Data.data | toJSON }}{{ end }}""" \
                                % backend_secret_path
            va_config += EXTRA_TEMPLATE % ("/tmp/backend/backend.tf.json",
                                           content_string)

        return va_config
