"""
stackl.globals
~~~~~~~~~~~~~~
This module provides global constants and values that should persist across api calls and stackl modules
"""
import json
import redis

from utils.general_utils import get_config_key

types_categories = ["configs", "items", "history"]
types_configs = [
    "environment", "location", "zone", "stack_application_template",
    "stack_infrastructure_template", "functional_requirement",
    "resource_requirement", "authentication", "policy_template"
]
types_items = [
    "stack_instance", "stack_template", "infrastructure_target", "service"
]
types_history = ["snapshot", "log"]
types = types_configs + types_items + types_history


class RedisCache():
    def __init__(self):
        self.redis_cache = None

    def connect(self):
        try:
            self.redis_cache = redis.StrictRedis(
                host=get_config_key("REDIS_HOST"), port=6379)
        except Exception:  #pylint: disable=broad-except
            self.redis_cache = redis.StrictRedis(host="localhost", port=6379)

    def get(self, key_name):
        return self.redis_cache.get(key_name)

    def set(self, key_name, value):
        self.redis_cache.set(key_name, value)

    def publish(self, channel, message):
        return self.redis_cache.publish(channel, message)

    def scan_iter(self, match=None, count=None, _type=None):
        return self.redis_cache.scan_iter(match, count, _type)

    def pubsub(self):
        return self.redis_cache.pubsub()

redis_cache = RedisCache()
alive_count_global = 0
task_queue_global = []


def initialize():
    redis_cache.connect()
    set_task_queue(task_queue_global)

def set_task_queue(task_queue):
    json_task_queue = json.dumps(task_queue)
    redis_cache.set("task_queue", json_task_queue)


def get_task_queue():
    json_task_queue = redis_cache.get("task_queue")
    task_queue = json.loads(json_task_queue)
    return task_queue
