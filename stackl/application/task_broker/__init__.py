import ast
import logging
import threading
from abc import ABC, abstractmethod

import globals

logger = logging.getLogger("STACKL_LOGGER")
from utils.general_utils import get_absolute_time_seconds


class TaskBroker(ABC):
    @abstractmethod
    def start_stackl(self, subscribe_channels=[], agent_broker=None):  # subscribe channels used by subclasses
        logger.debug("[{0}] Starting Task Broker for STACKL".format(logger.name))
        self.agent_broker = agent_broker
        self.task_signal = threading.Event()

    @abstractmethod
    def start_worker(self, subscribe_channels=[]):  # subscribe channels used by subclasses
        logger.debug("[{0}] Starting Task Broker for Worker".format(logger.name))

    @abstractmethod
    def give_task(self, task):
        pass

    @abstractmethod
    def get_task(self, tag):
        pass

    def remove_task_from_queue(self, task):
        task_queue = globals.get_task_queue()
        if task.topic == "result":
            logger.debug("[{2}] Task is ResultTask, removing the source_task '{0}' from task_queue '{1}'".format(
                task.source_task, task_queue, logger.name))
            id_task_to_remove = ast.literal_eval(task.source_task)["id"]
        else:
            id_task_to_remove = task.id
            logger.debug(
                "[{2}] Task has id '{0}', removing from task_queue '{1}'".format(id_task_to_remove, task_queue,
                                                                                 logger.name))
        for i in range(len(task_queue)):
            if task_queue[i]["id"] == id_task_to_remove:
                task_queue.pop(i)
                logger.debug(
                    "[{1}] Task with id '{0}' succesfully removed !".format(id_task_to_remove, logger.name))
                return
        logger.debug(
            "[{2}] Tried to remove task with id '{0}' but not found in queue '{1}' !".format(id_task_to_remove,
                                                                                             task_queue,
                                                                                             logger.name))

    def add_task_to_queue(self, task_obj):
        task_queue = globals.get_task_queue()
        task_queue.append(
            {"task": task_obj.as_json_string(), "id": task_obj.id, "start_time": get_absolute_time_seconds(),
             "wait_time": task_obj.wait_time})
        globals.set_task_queue(task_queue)
        logger.debug(
            "[{2}] Added task to queue. Task is '{0}'. Updated queue: '{1}'".format(task_obj, globals.get_task_queue(),
                                                                                    logger.name))
        self.task_signal.set()