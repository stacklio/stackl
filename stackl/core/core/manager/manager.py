"""Abstract manager module"""
from abc import ABC

from core.datastore.datastore_factory import DataStoreFactory


class Manager(ABC):
    """Abstract Manager Class"""

    def __init__(self):
        self.store = DataStoreFactory().get_store()
