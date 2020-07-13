from abc import ABC, abstractmethod

from core.datastore.datastore_factory import DataStoreFactory


class Manager(ABC):
    def __init__(self):
        self.store = DataStoreFactory().get_store()
