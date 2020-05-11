import json
import logging
import asyncio
from abc import ABC, abstractmethod

from enums.cast_type import CastType
from utils.general_utils import generate_random_string, get_hostname

logger = logging.getLogger("STACKL_LOGGER")


class Task(ABC):
    default_timeout_s = 30

    @property
    @abstractmethod
    def valid_subtypes(self):
        pass

    def __init__(self, task_data):
        self.source = None
        if type(task_data) == str:
            self._load_json_string(task_data)
        elif type(task_data) == dict:
            self._load_json_object(task_data)
        else:
            logger.info("[Task] task_data must be string or dict")
            raise Exception('task_data must be string or dict')

    def _load_json_string(self, json_string):
        self._load_json_object(json.loads(json_string))

    @abstractmethod
    def _load_json_object(self, json_obj):
        # Generic Task Attributes appear here
        self.topic = json_obj.get('topic', 'default_task')
        self.cast_type = json_obj.get('cast_type', CastType.ANYCAST.value)
        self.channel = json_obj.get('channel', 'all')
        self.id = generate_random_string()
        self._set_source(json_obj)
        self.args = json_obj.get('args', None)

        self.return_channel = json_obj.get('return_channel', None)
        self.timeout = json_obj.get('timeout', self.default_timeout_s)
        self.subtype = json_obj.get("subtype", [None])

    def _set_source(self, json_obj):
        source = json_obj.get('source', None)
        if source == None:
            self.source = get_hostname()
        else:
            self.source = source

    def get_attribute(self, attribute, default_value=None):
        if hasattr(self, attribute):
            return getattr(self, attribute)
        return default_value

    def get_channel(self):
        return self.channel

    def as_json_string(self):
        dictionary = self.__dict__
        # logger.info("[Task] Dictionary of task: {0}".format(dict))
        json_string = json.dumps(dictionary)
        # logger.info("[Task] json of task: {0}".format(json_string))
        return json_string