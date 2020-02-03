from abc import ABC, abstractmethod

import sys


from datastore.datastore_factory import DataStoreFactory

class Manager(ABC):

    def __init__(self, manager_factory):
        self.version = self.__get_version()
        self.store = DataStoreFactory().get_store()
        self.manager_factory = manager_factory

    def __get_version(self):
        try:
            with open(os.path.join('/etc/stackl_src/', 'VERSION')) as version_file:
                return version_file.read().strip()
        except:
            return 'v0.0.00000'