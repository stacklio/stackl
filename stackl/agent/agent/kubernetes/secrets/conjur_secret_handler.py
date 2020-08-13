from .base_secret_handler import SecretHandler


class ConjurSecretHandler(SecretHandler):
    def __init__(self, invoc, stack_instance, secret_format,
                 authenticator_client_container_name, conjur_appliance_url,
                 conjur_account, conjur_authn_token_file, conjur_authn_url,
                 conjur_authn_login, conjur_ssl_config_map):
        super().__init__(invoc, stack_instance, secret_format)
        self._invoc = invoc
        self._stack_instance = stack_instance
        self._authenticator_client_container_name = authenticator_client_container_name
        self._conjur_appliance_url = conjur_appliance_url
        self._conjur_account = conjur_account
        self._conjur_authn_token_file = conjur_authn_token_file
        self._conjur_authn_url = conjur_authn_url
        self._conjur_authn_login = conjur_authn_login
        self._conjur_ssl_config_map = conjur_ssl_config_map
        self._volumes = [{
            "name": "conjur-access-token",
            "type": "empty_dir",
            "mount_path": "/run/conjur"
        }]
        self._init_containers = [{
            "name": self._authenticator_client_container_name,
            "image": "cyberark/conjur-authn-k8s-client",
        }]
        self._env_list = {
            "CONTAINER_MODE": "init",
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
                "config_map_ref": self._conjur_ssl_config_map
            }
        }
