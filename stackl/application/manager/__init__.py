from abc import ABC

from datastore.datastore_factory import DataStoreFactory

class Manager(ABC):

    def __init__(self, manager_factory):
        self.store = DataStoreFactory().get_store()
        self.manager_factory = manager_factory