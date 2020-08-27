import os

from arq import create_pool
from arq.connections import RedisSettings

from core import config
from core.manager.document_manager import DocumentManager
from core.manager.snapshot_manager import SnapshotManager
from core.manager.stack_manager import StackManager

document_manager = DocumentManager()
snapshot_manager = SnapshotManager()
stack_manager = StackManager()


def get_document_manager():
    return document_manager


def get_snapshot_manager():
    return snapshot_manager


def get_stack_manager():
    return stack_manager


async def get_redis():
    return await create_pool(
        RedisSettings(host=config.settings.stackl_redis_host,
                      port=config.settings.stackl_redis_port))
