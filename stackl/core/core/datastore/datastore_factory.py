from loguru import logger

from core import config
from core.utils.stackl_singleton import Singleton


class DataStoreFactory(metaclass=Singleton):
    def __init__(self):
        self.store_type = config.settings.stackl_store

        logger.info(
            f"[DataStoreFactory] Creating config store with type: {self.store_type}"
        )
        if self.store_type == "Redis":
            from .redis_store import RedisStore
            self.store = RedisStore()
        elif self.store_type == "LFS" or self.store_type == "LocalFileSystemStore":
            lfs_path = config.settings.stackl_datastore_path
            from .local_file_system_store import LocalFileSystemStore
            self.store = LocalFileSystemStore(lfs_path)
        else:  # assume LFS
            logger.error("Invalid datastore setting")

    def get_store(self):
        return self.store
