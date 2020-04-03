from kubernetes import client

from handlers.base_secret_handler import SecretHandler

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
  {{- with secret "secret/data/infra/vmw?version=1" }}{{ .Data.data | %s }}{{ end }}
  EOH
  destination = "/tmp/secrets/secret.%s"
}
"""


def _create_agent_cm(self, name, namespace, cm_data):
    cm = client.V1ConfigMap()
    cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    cm.data = {"vault-agent-config.hcl": cm_data}
    return cm


class VaultSecretHandler:
    def __init__(self, secret_format: str):
        self.secret_format = secret_format.lower()

    # def handle_secret(self, kubernetes_body: client.V1Job):
    #     body = kubernetes_body
    #     vault_agent_env_list = [
    #         client.V1EnvVar(name="VAULT_ADDR", value="http://10.11.12.7:8200")
    #     ]
    #
    #     templated_vault_config = self.format_template()
    #     print(templated_vault_config)
    #     cm = _create_agent_cm(body.metadata.name + "-vault-agent",
    #                           body.metadata.namespace, templated_vault_config)
    #     volumes = []
    #
    #     vault_variables_vol = client.V1Volume(name="vault-variables")
    #     empty_dir = client.V1EmptyDirVolumeSource()
    #     empty_dir.medium = "Memory"
    #
    #     vault_config_map = client.V1ConfigMapVolumeSource()
    #     vault_config_map.name = cm.metadata.name
    #     vol_vault_config = client.V1Volume(name="vault-config")
    #     vol_vault_config.config_map = vault_config_map
    #
    #     volume_mounts = []
    #
    #     volume_vault_config_mount = client.V1VolumeMount(
    #         name="vault-config", mount_path="/etc/vault-config")
    #     volume_vault_variables_mount = client.V1VolumeMount(
    #         name="vault-variables", mount_path="/tmp/vault-variables")
    #
    #     volume_mounts.extend(
    #         [volume_vault_config_mount, volume_vault_variables_mount])
    #
    #     volumes.extend([vol_vault_config, vault_variables_vol])
    #
    #     body.spec.template.spec.containers[0].volume_mounts.append(
    #         volume_vault_variables_mount)
    #     body.spec.template.spec.volumes.extend(volumes)
    #     vault_agent_container = client.V1Container(
    #         name="vault-agent",
    #         image="vault",
    #         env=vault_agent_env_list,
    #         volume_mounts=volume_mounts,
    #         args=[
    #             "agent", "-config=/etc/vault-config/vault-agent-config.hcl",
    #             "-exit-after-auth"
    #         ])
    #
    #     return body, cm

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
