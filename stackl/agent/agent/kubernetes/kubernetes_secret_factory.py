from .secrets.base64_secret_handler import Base64SecretHandler
from .secrets.vault_secret_handler import VaultSecretHandler
from .secrets.conjur_secret_handler import ConjurSecretHandler
import os


def get_secret_handler(invoc, stack_instance, secret_format):
    if 'SECRET_HANDLER' in os.environ:
        secret_handler = os.environ['SECRET_HANDLER']
        if ('VAULT_ROLE' in os.environ and 'VAULT_ADDR' in os.environ
                and secret_handler.lower() == "vault"):
            vault_role = os.environ['VAULT_ROLE']
            vault_addr = os.environ['VAULT_ADDR']
            vault_mount_point = os.environ['VAULT_MOUNT_POINT']
            return VaultSecretHandler(invoc, stack_instance, vault_addr,
                                      secret_format, vault_role,
                                      vault_mount_point)
        elif secret_handler.lower() == "base64":
            return Base64SecretHandler(invoc, stack_instance, secret_format)
        elif secret_handler.lower() == "conjur":
            authenticator_client_container_name = os.environ[
                'AUTHENTICATOR_CLIENT_CONTAINER_NAME']
            conjur_appliance_url = os.environ['CONJUR_APPLIANCE_URL']
            conjur_account = os.environ['CONJUR_ACCOUNT']
            conjur_authn_token_file = os.environ['CONJUR_AUTHN_TOKEN_FILE']
            conjur_authn_url = os.environ['CONJUR_AUTHN_URL']
            conjur_authn_login = os.environ['CONJUR_AUTHN_LOGIN']
            conjur_ssl_config_map = os.environ['CONJUR_SSL_CONFIG_MAP']
            return ConjurSecretHandler(invoc, stack_instance, secret_format,
                                       authenticator_client_container_name,
                                       conjur_appliance_url, conjur_account,
                                       conjur_authn_token_file,
                                       conjur_authn_url, conjur_authn_login,
                                       conjur_ssl_config_map)
    else:
        return None
