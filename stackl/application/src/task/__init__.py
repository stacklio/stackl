import json
import logging
from abc import ABC, abstractmethod

from enums.cast_type import CastType

logger = logging.getLogger(__name__)
from utils.general_utils import generate_random_string, get_hostname


class Task(ABC):
    default_wait_time_s = 30

    @property
    @abstractmethod
    def valid_subtasks(self):
        pass

    def __init__(self, task_data):
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

        self.return_channel = json_obj.get('return_channel', None)
        self.wait_time = json_obj.get('wait_time', self.default_wait_time_s)
        self.subtasks = json_obj.get("subtasks", [None])

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
        dict = self.__dict__
        # logger.info("[Task] Dictionary of task: {0}".format(dict))
        json_string = json.dumps(dict)
        # logger.info("[Task] json of task: {0}".format(json_string))
        return json_string
