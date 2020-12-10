import json
from enum import IntEnum, unique
from os import environ

import redis
from loguru import logger

from core import config


# Modeled after HTTP Status Codes
@unique
class StatusCode(IntEnum):
    """Enums for stackl codes"""

    CONTINUE = 100  # Informational response: request was received and understood

    OK = 200  # Success Response: request was a success and the response depends on it
    CREATED = 201  # Success Response: request was a success and a document has been created
    ACCEPTED = 202  # Success Response: request was a success and is in progress

    # Client Errors
    BAD_REQUEST = 400  # the request was not processed due to a client-side error (
    UNAUTHORIZED = 401  # authentication is required but has failed or has not yet been provided
    FORBIDDEN = 403  # Client is not authorized to do the request
    NOT_FOUND = 404  # The request is not found
    CONFLICT = 409  # The request conflicts with the state of the server
    ROLLBACKED = 410  # The request conflicts with the state of the server

    # Server Errors
    INTERNAL_ERROR = 500  # STACKL has encountered an error it does not know how to handle.

    @classmethod
    def is_successful(cls, code):
        """checks if status code is between 200 and 400"""
        if isinstance(code, StatusCode):
            return 200 <= code < 400
        return 200 <= code < 400


class RedisStore():
    def __init__(self, host, port, db, password=''):
        self.redis = redis.Redis(host=host,
                                 port=port,
                                 password=password,
                                 db=db)

    class StoreResponse:
        """
      The :class:`StoreResponse <StoreResponse>` object,
      which contains a Store's response to a request. Modelled on the HTTP Response.
      Potentially other interesting attributes can be added from HTTP, such as elapsed,
      encoding, etc.
      """

        __attrs__ = ['content', 'status_code', 'reason']

        def __init__(self):
            self.content = False

            #: Integer Code of responded StoreResponse, with direct correlation
            # to HTTP Status, e.g. 404 or 200.
            self.status_code = None

            #: Textual reason of responded StoreResponse, e.g. "Not Found" or "OK".
            self.reason = None

        def __repr__(self):
            return '<StoreResponse. Status Code: {0}. Reason: {1}. Content: {2}>' \
                .format(self.status_code, self.reason, self.content)

    def _create_store_response(self,
                               status_code=StatusCode.OK,
                               reason=None,
                               content=None):
        """Helper method for creating a store response"""
        response = self.StoreResponse()
        response.status_code = status_code
        response.reason = reason
        response.content = content
        return response

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
            f"[RedisStore] get_all in '{document_key}' for type '{document_type}'"
        )
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

    def update_stack_instances(self, stack_instances):
        for stack_instance in stack_instances:
            for service_name, service in stack_instance['services'].items():
                for service_definition in service:
                    if not 'service' in service_definition:
                        service_definition['service'] = service_name
            self.put(stack_instance)


def upgrade():
    redis_instance = RedisStore(host=config.settings.stackl_redis_host,
                                port=config.settings.stackl_redis_port,
                                password=config.settings.stackl_redis_password,
                                db=0)

    stack_instances = redis_instance.get_all("items", "stack_instance")
    redis_instance.update_stack_instances(stack_instances.content)
    print(redis_instance.get_all("items", "stack_instance"))

