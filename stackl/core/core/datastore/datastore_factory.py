"""
Module for DataStoreFactory
"""
from loguru import logger

from core import config
from core.utils.stackl_singleton import Singleton
from .local_file_system_store import LocalFileSystemStore
from .redis_store import RedisStore


class DataStoreFactory(metaclass=Singleton):
    """Factory for choosing the datastore"""

    def __init__(self):
        self.store_type = config.settings.stackl_store

        logger.info(
            f"[DataStoreFactory] Creating config store with type: {self.store_type}"
        )
        if self.store_type == "Redis":
            self.store = RedisStore()
        elif self.store_type == "LFS" or self.store_type == "LocalFileSystemStore":
            lfs_path = config.settings.stackl_datastore_path
            self.store = LocalFileSystemStore(lfs_path)
        else:
            logger.error("Invalid datastore setting")

    def get_store(self):
        """Returns the store"""
        return self.store
