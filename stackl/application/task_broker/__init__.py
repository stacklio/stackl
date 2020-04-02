import ast
import logging
import threading
from abc import ABC, abstractmethod

import stackl_globals
from utils.general_utils import get_absolute_time_seconds

logger = logging.getLogger("STACKL_LOGGER")


class TaskBroker(ABC):
    def __init__(self):
        self.agent_broker = None
        self.task_signal = None

    @abstractmethod
    def start_stackl(
        self,
        subscribe_channels=None,
        agent_broker=None):  # subscribe channels used by subclasses
        logger.debug(f"[{logger.name}] Starting Task Broker for STACKL")
        self.agent_broker = agent_broker
        self.task_signal = threading.Event()

    @abstractmethod
    def start_worker(
        self,
        subscribe_channels=None):  # subscribe channels used by subclasses
        logger.debug(f"[{logger.name}] Starting Task Broker for Worker")

    @abstractmethod
    def give_task(self, task):
        pass

    @abstractmethod
    def get_task(self, tag):
        pass

    def remove_task_from_queue(self, task):
        task_queue = stackl_globals.get_task_queue()
        if task.topic == "result":
            logger.debug(
                f"[{logger.name}] Task is ResultTask, removing the source_task '{task.source_task}' from task_queue '{task_queue}'"
            )
            id_task_to_remove = ast.literal_eval(task.source_task)["id"]
        else:
            id_task_to_remove = task.id
            logger.debug(
                f"[{logger.name}] Task has id '{id_task_to_remove}', removing from task_queue '{task_queue}'"
            )
        for i in range(len(task_queue)):
            if task_queue[i]["id"] == id_task_to_remove:
                task_queue.pop(i)
                logger.debug(
                    f"[{logger.name}] Task with id '{id_task_to_remove}' succesfully removed !"
                )
                return
        logger.debug(
            f"[{logger.name}] Tried to remove task with id '{id_task_to_remove}' but not found in queue '{task_queue}' !"
        )

    def add_task_to_queue(self, task_obj):
        task_queue = stackl_globals.get_task_queue()
        task_queue.append({
            "task": task_obj.as_json_string(),
            "id": task_obj.id,
            "start_time": get_absolute_time_seconds(),
            "wait_time": task_obj.wait_time
        })
        stackl_globals.set_task_queue(task_queue)
        logger.debug(
            f"[{logger.name}] Added task to queue. Task is '{task_obj}'. Updated queue: '{stackl_globals.get_task_queue()}'"
        )
        self.task_signal.set()
