"""
Config module used for configuration data of stackl core
"""
from pydantic import BaseSettings


class Settings(BaseSettings): # pylint: disable=too-few-public-methods
    """
    Class containing all settings applicable to core component
    """
    stackl_store: str = "Redis"
    stackl_datastore_path: str = "/lfs-store"
    stackl_redis_type: str = "real"
    stackl_redis_host: str = "localhost"
    stackl_redis_port: int = 6379
    stackl_opa_host: str = "http://localhost:8181"
    rollback_enabled: bool = False


settings = Settings()
