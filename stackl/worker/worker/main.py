import json
import logging.config
import os
import threading

import stackl.stackl_globals as stackl_globals
from stackl.task_broker.task_broker_factory import TaskBrokerFactory  # pylint: disable=import-error
from stackl.utils.general_utils import get_hostname  # pylint: disable=import-error

from stackl.tasks.document_task import DocumentTask
from .manager.manager_factory import ManagerFactory  # pylint: disable=no-name-in-module,import-error

# initialize stackl globals
stackl_globals.initialize()

logger = logging.getLogger("STACKL_LOGGER")
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter('[[[%(asctime)s|%(message)s',
                              "%d.%m.%y|%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)


class Worker:
    def __init__(self):
        self.manager_factory = ManagerFactory()
        self.stack_manager = self.manager_factory.get_stack_manager()
        self.document_manager = self.manager_factory.get_document_manager()
        self.snapshot_manager = self.manager_factory.get_snapshot_manager()

        self.hostname = get_hostname()

        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

        logger.debug("[Worker] Initialised Worker.")

    def run(self):
        logger.debug("[Worker] Starting Worker")
        self.task_broker.start_worker(
            subscribe_channels=self.get_subscribe_channels())

        logger.debug("[Worker] Starting queue listen")
        self.start_task_popping()

    def start_task_popping(self):
        logger.info(
            "[Worker] start_task_popping. Started listen on message channel")
        while True:
            logger.info("[Worker] Waiting for items to appear in queue")
            tag = "common"
            task = self.task_broker.get_task(tag)

            logger.info(
                f"[Worker] Popped item. Type '{type(task)}'. Item: '{task}'")

            task_attr = json.loads(task)
            if task_attr["topic"] == "document_task":
                logger.info(
                    f"[Worker] DocumentTask with subtype \'{task_attr['subtype']}\'"
                )
                thread = threading.Thread(
                    target=self.document_manager.handle_task,
                    args=[DocumentTask.parse_obj(task_attr)])
                thread.start()
            elif task_attr["topic"] == "snapshot_task":
                logger.info(
                    f"[Worker] SnapshotTask with subtype \'{task_attr['subtype']}\'"
                )
                thread = threading.Thread(
                    target=self.snapshot_manager.handle_task, args=[task_attr])
                thread.start()
            elif task_attr["topic"] == "agent_task":
                # logger.info(
                #     f"[Worker] AgentTask with subtype \'{task_attr['subtype']}\'"
                # )
                # thread = threading.Thread(target=self.agent_broker.handle_task,
                #                           args=[task_attr])
                # thread.start()
                continue
            elif task_attr["topic"] == "stack_task":
                logger.info(
                    f"[Worker] StackTask with subtype \'{task_attr['subtype']}\'"
                )
                thread = threading.Thread(
                    target=self.stack_manager.handle_task, args=[task_attr])
                thread.start()

    def get_subscribe_channels(self):
        return ['all', 'worker', self.hostname]


def start():
    worker = Worker()
    worker.run()


if __name__ == '__main__':
    start()
