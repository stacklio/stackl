import json
import logging

import redis

from datastore import DataStore
from enums.stackl_codes import StatusCode
from utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")


class RedisStore(DataStore):
    def __init__(self):
        super(RedisStore, self).__init__()
        self.redis = redis.Redis(host=get_config_key("REDIS_HOST"),
                                 port=6379,
                                 db=0)

    def get(self, **keys):
        get_all = False
        if keys.get("document_name"):
            document_key = keys.get("category") + '/' + keys.get(
                "type") + '/' + keys.get("document_name")
        else:  # This means we need to get all the documents of the type
            get_all = True
            document_key = keys.get("category") + '/' + keys.get("type") + '/*'
        logger.debug(f"[RedisStore] get on key '{document_key}'")

        content = []
        if get_all:
            for key in self.redis.scan_iter(document_key):
                content.append(json.loads(self.redis.get(key)))
            response = self._create_store_response(status_code=StatusCode.OK,
                                                   content=content)
        else:
            redis_value = self.redis.get(document_key)
            if redis_value is None:
                response = self._create_store_response(
                    status_code=StatusCode.NOT_FOUND, content={})
            else:
                content = json.loads(self.redis.get(document_key))
                response = self._create_store_response(
                    status_code=StatusCode.OK, content=content)
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def get_configurator_file(self, configurator_file):
        document_key = 'statefiles/' + configurator_file
        redis_value = self.redis.get(document_key)
        if redis_value is None:
            response = self._create_store_response(
                status_code=StatusCode.NOT_FOUND, content={})
        else:
            response = self._create_store_response(
                status_code=StatusCode.CREATED,
                content=json.loads(redis_value))
        logger.debug(f"[RedisStore] StoreResponse for get: {response}")
        return response

    def put_configurator_file(self, name, configurator_file):
        document_key = 'statefiles/' + name
        self.redis.set(document_key, json.dumps(configurator_file))
        response = self._create_store_response(
            status_code=StatusCode.CREATED,
            content=json.loads(self.redis.get(document_key)))
        logger.debug(f"[RedisStore] StoreResponse for put: {response}")
        return response

    def delete_configurator_file(self, configurator_file):
        document_key = 'statefiles/' + configurator_file
        self.redis.delete(document_key)
        response = self._create_store_response(status_code=200, content={})
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
            "type") + '/' + keys.get("document_name")
        self.redis.delete(document_key)
        response = self._create_store_response(status_code=200, content={})
        logger.debug(f"[RedisStore] StoreResponse for delete: {response}")
        return response
