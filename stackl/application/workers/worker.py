import json
import os
import signal
import sys
import threading
import time

sys.path.append('/opt/stackl')

# Needed for globals
import stackl_globals

# initialize stackl globals
stackl_globals.initialize()

from utils.general_utils import get_hostname  # pylint: disable=import-error
from task_broker.task_broker_factory import TaskBrokerFactory  # pylint: disable=import-error
from manager.manager_factory import ManagerFactory  # pylint: disable=no-name-in-module,import-error
import logging.config

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
        self.user_manager = self.manager_factory.get_user_manager()

        self.thread_task_dict = {}

        self.hostname = get_hostname()

        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

        signal_list = [
            signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT
        ]
        logger.debug(f"[Worker] Adding signal handlers for {signal_list}")
        for sig in signal_list:
            signal.signal(sig, self.exit_handler)
        logger.debug("[Worker] Initialised Worker.")

    def run(self):
        try:
            logger.debug("[Worker] Starting Worker")
            time.sleep(5)
            self.task_broker.start_worker(
                subscribe_channels=self.get_subscribe_channels())

            logger.debug("[Worker] Starting queue listen")
            task_pop_thread = threading.Thread(target=self.start_task_popping,
                                               args=[])
            task_pop_thread.daemon = True  # ensures that this thread stops if worker stops
            task_pop_thread.start()

            while task_pop_thread.is_alive():
                time.sleep(10)
            logger.info(
                "[Worker] task_pop_thread was found dead. Killing Worker.")
        except Exception as e:  # TODO TBD during task rework
            logger.error(f"[Worker] Exception occured in Worker: {e}")

    def start_task_popping(self):
        logger.info(
            "[Worker] start_task_popping. Starting listening on redis queue")
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
                    target=self.document_manager.handle_task, args=[task_attr])
                thread.start()
                continue
            elif task_attr["topic"] == "snapshot_task":
                logger.info(
                    f"[Worker] SnapshotTask with subtype \'{task_attr['subtype']}\'"
                )
                thread = threading.Thread(
                    target=self.snapshot_manager.handle_task, args=[task_attr])
                thread.start()
                continue
            elif task_attr["topic"] == "agent_task":
                logger.info(
                    f"[Worker] AgentTask with subtype \'{task_attr['subtype']}\'"
                )
                thread = threading.Thread(target=self.agent_broker.handle_task,
                                          args=[task_attr])
                thread.start()
                continue
            elif task_attr["topic"] == "stack_task":
                # logger.info(
                #     f"[Worker] StackTask with subtype \'{task_attr['subtype']}\'"
                # )
                # thread = threading.Thread(
                #     target=self.stack_manager.handle_task, args=[task_attr])
                # thread.start()
                continue

    def get_subscribe_channels(self):
        return ['all', 'worker', self.hostname]

    def exit_handler(self, signum=None):
        logger.info(f"[Worker] Signal handler called with signal {signum}")
        logger.info("[Worker] flushing queue")
        # tasks = self.queue.lrange('task_' + self.hostname + ':process', 0 , -1)
        # if tasks:
        #     for task in tasks:
        #         logger.info("[Worker] pushing task to queue: {0}".format("task_" + "common"+':process'))
        #         self.queue.lpush("task_" + "common"+':process', task)
        # self.queue.delete('task_'+ self.hostname + ':process')
        logger.info("[Worker] Flushing done")
        sys.exit(0)


if __name__ == '__main__':
    worker = Worker()
    worker.run()
