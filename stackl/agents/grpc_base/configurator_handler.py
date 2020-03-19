import logging

from abc import ABC, abstractmethod

class ConfiguratorHandler(ABC):

    @abstractmethod
    def create_job_command(self, handle_obj):
        return None

    @abstractmethod
    def create_delete_command(self, handle_obj):
        return None

    @abstractmethod
    def id_generator(self, handle_obj):
        return None
