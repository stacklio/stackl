"""
stackl.globals
~~~~~~~~~~~~~~
This module provides global constants and values that should persist across api calls and stackl modules
"""

import json
import time

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
types_history = [
    "snapshot", "log"
]
types = types_configs + types_items + types_history

redis_cache = None
alive_count_global = 0
task_queue_global = []


def initialize():
    global redis_cache
    try:
        time.sleep(5)
        redis_cache = redis.StrictRedis(host=get_config_key("REDIS_HOST"),
                                        port=6379)
    except Exception:  #TODO TBD Fix during Task rework
        redis_cache = redis.StrictRedis(host="localhost", port=6379)
    set_task_queue(task_queue_global)
    set_alive_count(alive_count_global)


def set_task_queue(task_queue):
    json_task_queue = json.dumps(task_queue)
    redis_cache.set("task_queue", json_task_queue)


def get_task_queue():
    json_task_queue = redis_cache.get("task_queue")
    task_queue = json.loads(json_task_queue)
    return task_queue


def set_alive_count(alive_count):
    json_alive_count = json.dumps(alive_count)
    redis_cache.set("alive_count", json_alive_count)


def get_alive_count():
    json_alive_count = redis_cache.get("alive_count")
    alive_count = json.loads(json_alive_count)
    return alive_count
