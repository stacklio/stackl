"""
Config module used for configuration data of stackl core
"""
import logging

from loguru import logger
from pydantic import BaseSettings
from typing import List, Tuple


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion. see
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth,
                   exception=record.exc_info).log(level, record.getMessage())


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """
    Class containing all settings applicable to core component
    """
    log_level: str = "DEBUG"

    # Datastore options
    stackl_store: str = "Redis"
    stackl_datastore_path: str = "/lfs-store"

    # Redis options
    stackl_redis_type: str = "sentinel"
    stackl_redis_host: str = "localhost"
    stackl_redis_password: str = None
    stackl_redis_port: int = 6379
    stackl_redis_sentinel_master: str = "stackl"
    stackl_redis_hosts: List[Tuple[str, int]] = []  # '[["localhost", 26379]]'

    # OPA options
    stackl_opa_host: str = "http://localhost:8181"

    # Extra functionality
    rollback_enabled: bool = False

    # Elastic APM options
    elastic_apm_enabled: bool = False


settings = Settings()
