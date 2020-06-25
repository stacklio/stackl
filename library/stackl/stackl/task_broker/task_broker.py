import asyncio
import json
import logging
import threading
from abc import ABC, abstractmethod

import stackl.stackl_globals as stackl_globals
from stackl.enums.stackl_codes import StatusCode
from stackl.utils.general_utils import get_absolute_time_seconds

logger = logging.getLogger("STACKL_LOGGER")
empty_result_dict = {"task_id_of_result": None, "result": None}


class TaskBroker(ABC):
    def __init__(self):
        self.agent_broker = None
        self.manager_factory = None
        self.stack_manager = None
        self.document_manager = None
        self.snapshot_manager = None
        self.user_manager = None

        self.task_signal = threading.Event()
        self.task_signal.clear()
        self.task_monitor_thread = None

        self.asyncio_task_completed = asyncio.Event()
        self.asyncio_task_completed.clear()

        self.result_dict = empty_result_dict

    @abstractmethod
    def give_task(self, task_obj):
        pass

    @abstractmethod
    def get_task(self, tag):
        pass

    def remove_task_from_queue(self, id_task_to_remove):
        task_queue = stackl_globals.get_task_queue()
        for (index, _) in enumerate(task_queue):
            if task_queue[index]["id"] == id_task_to_remove:
                task_queue.pop(index)
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
            "task": task_obj.json(),
            "id": task_obj.id,
            "start_time": get_absolute_time_seconds(),
            "timeout": task_obj.timeout,
        })
        stackl_globals.set_task_queue(task_queue)
        logger.debug(
            f"[TaskBroker] Added task to queue. Task_id '{task_obj.id}'. Updated queue: '{stackl_globals.get_task_queue()}'"
        )
        self.task_signal.set()

    # Run in thread
    def task_queue_monitor(self):
        try:
            while True:
                earliest_task_timer = self._get_earliest_timeout_task()
                task_queue = stackl_globals.get_task_queue()
                logger.debug(
                    f"[TaskBroker] task_queue_monitor. len task_queue is '{len(task_queue)}'. Waiting until task added or earliest_task_timer '{earliest_task_timer['timeout']}'"
                )
                self.task_signal.wait(timeout=earliest_task_timer["timeout"])

                new_earliest_task_timer = self._get_earliest_timeout_task()
                logger.debug(
                    f"[TaskBroker] task_queue_monitor. Either a timeout '{new_earliest_task_timer['timeout']}' or new task added '{self.task_signal.is_set()}'"
                )
                if new_earliest_task_timer["timeout"] is not None:
                    if new_earliest_task_timer["timeout"] <= 0:
                        logger.debug(
                            f"[TaskBroker] task_queue_monitor. Timeout. Checking if the waiting task is still in queue"
                        )
                        if new_earliest_task_timer["task_id"] in [
                                task["id"] for task in task_queue
                        ]:
                            self.initiate_rollback_task(
                                new_earliest_task_timer["task_id"])
                            self.remove_task_from_queue(
                                new_earliest_task_timer["task_id"])

                            self.result_dict[
                                "task_id_of_result"] = new_earliest_task_timer[
                                    "task_id"]
                            self.result_dict["result"] = StatusCode.ROLLBACKED
                            self.asyncio_task_completed.set()
                self.task_signal.clear()
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                f"[TaskBroker] task_queue_monitor. Encountered an issue. Exception: '{e}'"
            )

    # Run in thread
    def _get_earliest_timeout_task(self):
        task_queue = stackl_globals.get_task_queue()
        list_task_timeouts = [
            (task["id"], task["timeout"] -
             (get_absolute_time_seconds() - task["start_time"]))
            for task in task_queue
        ]
        logger.debug(
            f"[TaskBroker] list_of_task_timeouts: '{list_task_timeouts}'")
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

    def initiate_rollback_task(self, id_task_to_rollback):
        logger.debug(
            f"[TaskBroker] rollback_task. Task with id '{id_task_to_rollback}' did not compleet succesfully. Initiating rollback and removing from queue."
        )
        task_queue = stackl_globals.get_task_queue()
        for (index, _) in enumerate(task_queue):
            if task_queue[index]["id"] == id_task_to_rollback:
                task_to_rollback = json.loads(task_queue[index]["task"])
                logger.debug(
                    f"[TaskBroker] rollback_task. task_to_rollback: '{task_to_rollback}'."
                )

                if task_to_rollback["topic"] == "document_task":
                    logger.info(
                        f"[TaskBroker] Rollback DocumentTask with subtype \'{task_to_rollback['subtype']}\'"
                    )
                    thread = threading.Thread(
                        target=self.document_manager.rollback_task,
                        args=[task_to_rollback])
                    thread.start()
                elif task_to_rollback["topic"] == "snapshot_task":
                    logger.info(
                        f"[TaskBroker] Rollback SnapshotTask with subtype \'{task_to_rollback['subtype']}\'"
                    )
                    thread = threading.Thread(
                        target=self.snapshot_manager.rollback_task,
                        args=[task_to_rollback])
                    thread.start()
                elif task_to_rollback["topic"] == "agent_task":
                    logger.info(
                        f"[TaskBroker] Rollback AgentTask with subtype \'{task_to_rollback['subtype']}\'"
                    )
                    thread = threading.Thread(
                        target=self.agent_broker.rollback_task,
                        args=[task_to_rollback])
                    thread.start()
                elif task_to_rollback["topic"] == "stack_task":
                    logger.info(
                        f"[TaskBroker] Rollback StackTask with subtype \'{task_to_rollback['subtype']}\'"
                    )
                    thread = threading.Thread(
                        target=self.stack_manager.rollback_task,
                        args=[task_to_rollback])
                    thread.start()
            return
