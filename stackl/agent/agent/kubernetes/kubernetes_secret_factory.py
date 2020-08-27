from .secrets.base64_secret_handler import Base64SecretHandler
from .secrets.vault_secret_handler import VaultSecretHandler
from .secrets.conjur_secret_handler import ConjurSecretHandler
import os

from .. import config


def get_secret_handler(invoc, stack_instance, secret_format):
    secret_handler = config.settings.secret_handler
    if (config.settings.vault_role and config.settings.vault_addr
            and secret_handler.lower() == "vault"):
        vault_role = config.settings.vault_role
        vault_addr = config.settings.vault_addr
        vault_mount_point = config.settings.vault_mount_point
        return VaultSecretHandler(invoc, stack_instance, vault_addr,
                                  secret_format, vault_role,
                                  vault_mount_point)
    elif secret_handler.lower() == "base64":
        return Base64SecretHandler(invoc, stack_instance, secret_format)
    elif secret_handler.lower() == "conjur":
        authenticator_client_container_name = config.settings.authenticator_client_container_name
        conjur_appliance_url = config.settings.conjur_appliance_url
        conjur_account = config.settings.conjur_account
        conjur_authn_token_file = config.settings.conjur_authn_token_file
        conjur_authn_url = config.settings.conjur_authn_url
        conjur_authn_login = config.settings.conjur_authn_login
        conjur_ssl_config_map = config.settings.conjur_ssl_config_map
        conjur_ssl_config_map_key = config.settings.conjur_ssl_config_map_key
        conjur_verify = config.settings.conjur_verify
        return ConjurSecretHandler(
            invoc, stack_instance, secret_format,
            authenticator_client_container_name, conjur_appliance_url,
            conjur_account, conjur_authn_token_file, conjur_authn_url,
            conjur_authn_login, conjur_ssl_config_map,
            conjur_ssl_config_map_key, conjur_verify)
    else:
        return None
