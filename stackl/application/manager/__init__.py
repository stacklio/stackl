from abc import ABC

from datastore.datastore_factory import DataStoreFactory


class Manager(ABC):
    def __init__(self):
        self.store = DataStoreFactory().get_store()
