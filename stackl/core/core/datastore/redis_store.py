import json

import redis
from core.enums.stackl_codes import StatusCode
from loguru import logger

from core import config
from .datastore import DataStore


class RedisStore(DataStore):
    def __init__(self):
        super(RedisStore, self).__init__()
        self.redis = redis.Redis(host=config.settings.stackl_redis_host,
                                 port=config.settings.stackl_redis_port,
                                 db=0)

    def get(self, **keys):
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

    def get_all(self, category, type, wildcard_prefix=""):
        document_key = f"{category}/{type}/{wildcard_prefix}*"
        logger.debug(
            f"[RedisStore] get_all in '{document_key}' for type '{type}'")
        content = []
        for key in self.redis.scan_iter(document_key):
            content.append(json.loads(self.redis.get(key)))
        response = self._create_store_response(status_code=StatusCode.OK,
                                               content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def get_history(self, category, type, name):
        document_key = category + '/' + type + '/' + name
        logger.debug(
            f"[RedisStore] get_history in '{document_key}' for type '{type}'")
        content = []
        for key in self.redis.scan_iter(document_key):
            content.append(json.loads(self.redis.get(key)))
        response = self._create_store_response(status_code=StatusCode.OK,
                                               content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def put(self, file):
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
        document_key = keys.get("category") + '/' + keys.get(
            "type") + '/' + keys.get("name")
        self.redis.delete(document_key)
        response = self._create_store_response(status_code=200, content={})
        logger.debug(f"[RedisStore] StoreResponse for delete: {response}")
        return response
