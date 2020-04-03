from kubernetes import client

vault_agent_config = """
exit_after_auth = false
pid_file = "/home/vault/pidfile"
auto_auth {
    method "kubernetes" {
        mount_path = "auth/kubernetes"
        config = {
            role = "stackl"
        }
    }
    sink "file" {
        config = {
            path = "/home/vault/.vault-token"
        }
    }
}

template {
  contents = <<EOH
  {{- with secret "secret/data/infra/vmw2?version=1" }}{{ .Data.data | %s }}{{ end }}
  EOH
  destination = "/tmp/secrets/secret.%s"
}
"""


def _create_agent_cm(name, namespace, cm_data):
    cm = client.V1ConfigMap()
    cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    cm.data = {"vault-agent-config.hcl": cm_data}
    return cm


class VaultSecretHandler:
    def __init__(self, secret_format: str):
        self.secret_format = secret_format.lower()

    def get_volumes(self):
        return [{
            'name': 'vault-agent-config',
            'mount_path': '/etc/vault-config',
            'type': 'config_map',
            'data': {
                'vault-agent-config.hcl': self.format_template()
            }
        }]

    def get_init_containers(self):
        return [{
            "name":
            "vault-agent",
            "image":
            "vault",
            "args": [
                "agent", "-config=/etc/vault-config/vault-agent-config.hcl",
                "-exit-after-auth"
            ]
        }]

    def get_env_list(self):
        return {"VAULT_ADDR": "http://10.11.12.7:8200"}

    def format_template(self):
        format_str = self._get_format()
        return vault_agent_config % (format_str, self.secret_format)

    def _get_format(self):
        if self.secret_format == "json":
            return "toJSON"
        if self.secret_format == "yaml" or self.secret_format == "yml":
            return "toYAML"
        if self.secret_format == "toml":
            return "toTOML"
