import types
from abc import ABC

from stackl.agents.kubernetes_agent.handlers.base_secret_handler import SecretHandler


class VaultSecretHandler(SecretHandler):

    def get_secrets(self):
        return {}
