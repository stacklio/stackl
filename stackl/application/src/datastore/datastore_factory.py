import sys


from logger import Logger
from utils.stackl_singleton import Singleton
from utils.general_utils import get_config_key

class DataStoreFactory(metaclass=Singleton):

    def __init__(self):
        self.store_type = get_config_key('STORE')
        self.logger = Logger("DataStoreFactory")
        self.logger.info("[DataStoreFactory] Creating config store with type: " + self.store_type)
        if self.store_type == "Redis":
            pass 
        elif self.store_type == "S3":
            pass
        elif self.store_type == "CouchDB":
            from datastore.couchDB_store import CouchDBStore
            self.store = CouchDBStore()
        elif self.store_type == "LFS" or type == "LocalFileSystemStore":
            from datastore.local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore('/lfs_test_store/')
        else: #assume LFS
            from datastore.local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore('/lfs_test_store/')

    def get_store(self):
        return self.store
