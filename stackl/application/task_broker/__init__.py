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

        self.task_monitor_thread = threading.Thread(name="Task Monitor Thread", target=self.task_queue_monitor,
                                                    args=[self.task_signal])
        self.task_monitor_thread.start()

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

    # Run in thread
    def task_queue_monitor(self, task_signal):
        try:
            while True:
                earliest_task_timer = self._determine_wait_time()
                task_queue = globals.get_task_queue()
                logger.debug(
                    "[{2}] Monitor_threads. len task_queue is '{0}'. Waiting until task added or earliest_task_timer '{1}'".format(
                        len(task_queue), earliest_task_timer["wait_time"], logger.name))

                task_signal.wait(timeout=earliest_task_timer["wait_time"])

                logger.debug(
                    "[{0}] Wait time expired or new task added. Checking if any tasks expired".format(logger.name))
                earliest_task_timer = self._determine_wait_time()
                if earliest_task_timer["wait_time"] < 0:
                    logger.debug("[{0}] Wait time expired. Checking if the waiting task is still in queue".format(
                        logger.name))
                    if earliest_task_timer["task_id"] in [task["id"] for task in task_queue]:
                        raise Exception("A task expired! Rollback of task")
                        # TODO implement rollback
        except Exception as e:
            logger.error(
                "[{0}] Monitor threads encountered an issue. Exception: '{1}'".format(logger.name, e))

    # Run in thread
    def _determine_wait_time(self):
        task_queue = globals.get_task_queue()
        if len(task_queue) == 0:
            earliest_task_timer = {"id": "None", "wait_time": None}  # block indefinitely
        else:
            list_of_wait_time_tasks = [
                (task["id"], task["wait_time"] - (get_absolute_time_seconds() - task["start_time"])) for task in
                task_queue]
            logger.debug("[{1}] list_of_wait_time_tasks: '{0}'".format(list_of_wait_time_tasks, logger.name))
            earliest_task_tuple = min(list_of_wait_time_tasks, key=lambda n: n[1])
            earliest_task_timer = {"id": earliest_task_tuple[0], "wait_time": earliest_task_tuple[1]}
        logger.debug("[{1}] determine_wait_time determined earliest_task_timer: '{0}'".format(earliest_task_timer,
                                                                                              logger.name))
        return earliest_task_timer
