import json
import logging

import redis

from .datastore import DataStore
from stackl.enums.stackl_codes import StatusCode
from stackl.utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")


class RedisStore(DataStore):
    def __init__(self):
        super(RedisStore, self).__init__()
        self.redis = redis.Redis(host=get_config_key("REDIS_HOST"),
                                 port=6379,
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

    def get_all(self, category, type_name):
        document_key = category + '/' + type_name + '/*'
        logger.debug(
            f"[RedisStore] get_all in '{document_key}' for type '{type_name}'")
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
