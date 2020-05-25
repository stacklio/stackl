from abc import ABC, abstractmethod

from datastore.datastore_factory import DataStoreFactory


class Manager(ABC):
    def __init__(self):
        self.store = DataStoreFactory().get_store()

    @abstractmethod
    def handle_task(self, task):
        pass

    @abstractmethod
    def rollback_task(self, task):
        pass