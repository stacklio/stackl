import logging

from core.utils.general_utils import get_config_key
from core.utils.stackl_singleton import Singleton

from loguru import logger


class DataStoreFactory(metaclass=Singleton):
    def __init__(self):
        self.store_type = get_config_key('STORE')

        logger.info(
            f"[DataStoreFactory] Creating config store with type: {self.store_type}"
        )
        if self.store_type == "Redis":
            from .redis_store import RedisStore
            self.store = RedisStore()
        elif self.store_type == "LFS" or self.store_type == "LocalFileSystemStore":
            lfs_path = get_config_key('DATASTORE_PATH')
            from .local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore(lfs_path)
        else:  # assume LFS
            lfs_path = get_config_key('DATASTORE_PATH')
            from .local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore(lfs_path)

    def get_store(self):
        return self.store
