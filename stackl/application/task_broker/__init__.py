import ast
import logging
import threading
import asyncio
from abc import ABC, abstractmethod
import json

import stackl_globals
from utils.general_utils import get_absolute_time_seconds

logger = logging.getLogger("STACKL_LOGGER")

empty_result_dict = {"result_for_source_task_id": None, "result": None}


class TaskBroker(ABC):
    def __init__(self):
        self.agent_broker = None
        self.task_signal = threading.Event()
        self.asyncio_task_completed = asyncio.Event()
        self.asyncio_task_completed.clear()
        self.result_dict = empty_result_dict

    @abstractmethod
    def start_stackl(
        self,
        subscribe_channels=None,
        agent_broker=None):  # subscribe channels used by subclasses
        logger.debug(f"[TaskBroker] Starting Task Broker for STACKL")
        self.agent_broker = agent_broker

    @abstractmethod
    def start_worker(
        self,
        subscribe_channels=None):  # subscribe channels used by subclasses
        logger.debug(f"[TaskBroker] Starting Task Broker for Worker")

    @abstractmethod
    def give_task(self, task_obj):
        pass

    @abstractmethod
    def get_task(self, tag):
        pass

    def remove_task_from_queue(self, id_task_to_remove):
        task_queue = stackl_globals.get_task_queue()
        for i in range(len(task_queue)):
            if task_queue[i]["id"] == id_task_to_remove:
                task_queue.pop(i)
                logger.debug(
                    f"[TaskBroker] Task with id '{id_task_to_remove}' succesfully removed !"
                )
            return
        logger.debug(
            f"[TaskBroker] Tried to remove task with id '{id_task_to_remove}' but not found in queue '{task_queue}' !"
        )

    def add_task_to_queue(self, task_obj):
        task_queue = stackl_globals.get_task_queue()
        task_queue.append({
            "task": task_obj.as_json_string(),
            "id": task_obj.id,
            "start_time": get_absolute_time_seconds(),
            "timeout": task_obj.timeout,
        })
        stackl_globals.set_task_queue(task_queue)
        logger.debug(
            f"[TaskBroker] Added task to queue. Task is '{task_obj}'. Updated queue: '{stackl_globals.get_task_queue()}'"
        )
        self.task_signal.set()

    def process_result_task(self, result_task):
        source_task_id = ast.literal_eval(result_task.source_task)["id"]
        logger.debug(
            f"[TaskBroker] add_result_task_to_queue. Removing source task '{source_task_id}' and returning result '{result_task.result}'"
        )
        self.remove_task_from_queue(source_task_id)
        self.result_dict["result_for_source_task_id"] = source_task_id
        self.result_dict["result"] = result_task.result

        self.asyncio_task_completed.set()

    async def get_task_result(self, task_id):
        while True:
            self.asyncio_task_completed.clear()
            if task_id == self.result_dict["result_for_source_task_id"]:
                result = self.result_dict["result"]
                logger.debug(
                    f"[TaskBroker] get_task_result. A task completed. Task  '{task_id}' has result: '{result}'."
                )

                self.result_dict = empty_result_dict
                return result
            else:
                logger.debug(
                    f"[TaskBroker] get_task_result. No result yet, waiting.")
                await self.asyncio_task_completed.wait()
