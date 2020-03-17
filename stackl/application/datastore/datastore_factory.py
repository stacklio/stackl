import logging

from utils.general_utils import get_config_key
from utils.stackl_singleton import Singleton


logger = logging.getLogger("STACKL_LOGGER")


class DataStoreFactory(metaclass=Singleton):

    def __init__(self):
        self.store_type = get_config_key('STORE')

        logger.info("[DataStoreFactory] Creating config store with type: " + self.store_type)
        if self.store_type == "Redis":
            from datastore.redis_store import RedisStore
            self.store = RedisStore()
        elif self.store_type == "S3":
            pass
        elif self.store_type == "LFS" or self.store_type == "LocalFileSystemStore":
            lfs_path = get_config_key('DATASTORE_PATH')
            from datastore.local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore(lfs_path)
        else:  # assume LFS
            from datastore.local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore(lfs_path)

    def get_store(self):
        return self.store
