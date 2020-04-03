from secrets.base64_secret_handler import Base64SecretHandler
from secrets.vault_secret_handler import VaultSecretHandler
import os


def get_secret_handler(invoc, stack_instance, secret_format):
    if 'SECRET_HANDLER' in os.environ:
        secret_handler = os.environ['SECRET_HANDLER']
        if ('VAULT_ROLE' in os.environ and 'VAULT_ADDR' in os.environ
                and secret_handler.lower() == "vault"):
            vault_role = os.environ['VAULT_ROLE']
            vault_addr = os.environ['VAULT_ADDR']
            return VaultSecretHandler(invoc, stack_instance, vault_addr,
                                      secret_format, vault_role)
        elif secret_handler.lower() == "base64":
            return Base64SecretHandler(invoc, stack_instance, secret_format)
    else:
        return None
