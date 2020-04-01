import types
from abc import ABC, abstractmethod


class SecretHandler(ABC):

    @abstractmethod
    def get_secrets(self):
        pass
