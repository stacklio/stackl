import ast
import logging
import threading
import asyncio
from abc import ABC, abstractmethod
import json

import stackl_globals
from utils.general_utils import get_absolute_time_seconds

logger = logging.getLogger("STACKL_LOGGER")

empty_result_dict = {"result_for_task_id": None, "result": None}


class TaskBroker(ABC):
    def __init__(self):
        self.agent_broker = None

        self.task_signal = threading.Event()
        self.task_signal.clear()
        self.task_monitor_thread = None

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

        self.task_monitor_thread = threading.Thread(
            name="Task Monitor Thread",
            target=self.task_queue_monitor,
            args=[])
        self.task_monitor_thread.start()

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
                stackl_globals.set_task_queue(task_queue)
            return
        logger.debug(
            f"[TaskBroker] Tried to remove task with id '{id_task_to_remove}' but not found in queue '{task_queue}'"
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
            f"[TaskBroker] Added task to queue. Task_id '{task_obj.id}'. Updated queue: '{stackl_globals.get_task_queue()}'"
        )
        self.task_signal.set()

    def process_result_task(self, result_task):
        source_task_id = ast.literal_eval(result_task.source_task)["id"]
        logger.debug(
            f"[TaskBroker] process_result_task. Removing source task '{source_task_id}' and returning result '{result_task.result}'"
        )
        self.remove_task_from_queue(source_task_id)
        self.result_dict["result_for_task_id"] = source_task_id
        self.result_dict["result"] = result_task.result

        self.asyncio_task_completed.set()

    async def get_task_result(self, task_id):
        while True:
            self.asyncio_task_completed.clear()
            if task_id == self.result_dict["result_for_task_id"]:
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

    # Run in thread
    def task_queue_monitor(self):
        try:
            while True:
                earliest_task_timer = self._get_earliest_timeout_task()
                task_queue = stackl_globals.get_task_queue()
                logger.debug(
                    f"[TaskBroker] Monitor_threads. len task_queue is '{len(task_queue)}'. Waiting until task added or earliest_task_timer '{earliest_task_timer['timeout']}'"
                )

                self.task_signal.wait(timeout=earliest_task_timer["timeout"])

                logger.debug(
                    f"[TaskBroker] Either a timeout '{not self.task_signal.is_set()}' or new task added '{self.task_signal.is_set()}'"
                )
                new_earliest_task_timer = self._get_earliest_timeout_task()
                if new_earliest_task_timer["timeout"] is not None:
                    if new_earliest_task_timer["timeout"] < 0:
                        logger.debug(
                            f"[TaskBroker] Timeout. Checking if the waiting task is still in queue"
                        )
                        if new_earliest_task_timer["task_id"] in [
                                task["id"] for task in task_queue
                        ]:
                            self.remove_task_from_queue(
                                new_earliest_task_timer["task_id"])
                            self.result_dict[
                                "result_for_task_id"] = new_earliest_task_timer[
                                    "task_id"]
                            self.result_dict[
                                "result"] = "Timeout expired. Rolling back."
                            self.asyncio_task_completed.set()
                self.task_signal.clear()
        except Exception as e:
            logger.error(
                f"[TaskBroker] Monitor threads encountered an issue. Exception: '{e}'"
            )

    # Run in thread
    def _get_earliest_timeout_task(self):
        task_queue = stackl_globals.get_task_queue()
        list_task_timeouts = [
            (task["id"], task["timeout"] -
                (get_absolute_time_seconds() - task["start_time"]))
            for task in task_queue
        ]
        # logger.debug(
        #     f"[TaskBroker] list_of_task_timeouts: '{list_task_timeouts}'")
        if list_task_timeouts:
            earliest_task_tuple = min(list_task_timeouts, key=lambda n: n[1])
            earliest_task_timer = {
                "task_id": earliest_task_tuple[0],
                "timeout": earliest_task_tuple[1]
            }
            # logger.debug(
            #     f"[TaskBroker] _determine_earliest_timeout. Earliest_task_timer: '{earliest_task_timer}'"
            # )
            return earliest_task_timer
        else:
            return {"id": "None", "timeout": None}
