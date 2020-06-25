import random
import string
from abc import ABC, abstractmethod


class ConfiguratorHandler(ABC):
    @abstractmethod
    def handle(self, invocation, action):
        return None

    @abstractmethod
    def create_job_command(self, handle_obj):
        return None

    @abstractmethod
    def create_delete_command(self, handle_obj):
        return None

    def id_generator(self,
                     size=12,
                     chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
