"""
Redis datastore module
"""
import json

import redis
from loguru import logger
from redislite import Redis

from core import config
from core.enums.stackl_codes import StatusCode
from .datastore import DataStore


class RedisStore(DataStore):
    """Implementation of Redis datastore"""

    def __init__(self):
        super().__init__()
        if config.settings.stackl_redis_type == "fake":
            logger.info("Using fake client")

            self.redis = Redis()
        else:
            self.redis = redis.Redis(host=config.settings.stackl_redis_host,
                                     port=config.settings.stackl_redis_port,
                                     password=config.settings.stackl_redis_password,
                                     db=0)

    def get(self, **keys):
        """Gets a document from a redis instance"""
        document_key = keys.get("category") + '/' + keys.get(
            "type") + '/' + keys.get("name")
        logger.debug(f"[RedisStore] get on key '{document_key}'")

        redis_value = self.redis.get(document_key)
        if redis_value is None:
            response = self._create_store_response(
                status_code=StatusCode.NOT_FOUND, content={})
        else:
            content = json.loads(self.redis.get(document_key))
            response = self._create_store_response(status_code=StatusCode.OK,
                                                   content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def get_all(self, category, document_type, wildcard_prefix=""):
        """Gets all documents of a type from a Redis"""
        document_key = f"{category}/{document_type}/{wildcard_prefix}*"
        logger.debug(
            f"[RedisStore] get_all in '{document_key}' for type '{document_type}'")
        content = []
        for key in self.redis.scan_iter(document_key):
            content.append(json.loads(self.redis.get(key)))
        response = self._create_store_response(status_code=StatusCode.OK,
                                               content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def get_history(self, category, document_type, name):
        """Gets the snapshots of document from Redis"""
        document_key = category + '/' + document_type + '/' + name
        logger.debug(
            f"[RedisStore] get_history in '{document_key}' for type '{document_type}'")
        content = []
        for key in self.redis.scan_iter(document_key):
            content.append(json.loads(self.redis.get(key)))
        response = self._create_store_response(status_code=StatusCode.OK,
                                               content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def put(self, file):
        """Puts a document in Redis"""
        document_key = file.get("category") + '/' + file.get(
            "type") + '/' + file["name"]
        logger.debug(f"[RedisStore] put on '{document_key}' with file {file}")
        self.redis.set(document_key, json.dumps(file))
        response = self._create_store_response(
            status_code=StatusCode.CREATED,
            content=json.loads(self.redis.get(document_key)))
        logger.debug(f"[RedisStore] StoreResponse for put: {response}")
        return response

    def delete(self, **keys):
        """Deletes a document in Redis"""
        document_key = keys.get("category") + '/' + keys.get(
            "type") + '/' + keys.get("name")
        self.redis.delete(document_key)
        response = self._create_store_response(status_code=200, content={})
        logger.debug(f"[RedisStore] StoreResponse for delete: {response}")
        return response
