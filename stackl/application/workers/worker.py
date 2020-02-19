import json
import os
import signal
import sys
import threading
import time

# Needed for globals
sys.path.append('/opt/stackl')

from utils.general_utils import get_hostname  # pylint: disable=import-error
from manager.manager_factory import ManagerFactory  # pylint: disable=no-name-in-module,import-error
import logging.config

logger = logging.getLogger("STACKL_LOGGER")
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter(
    "{'time':'%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}")
ch.setFormatter(formatter)
logger.addHandler(ch)
from task_broker.task_broker_factory import TaskBrokerFactory  # pylint: disable=import-error
from agent_broker.agent_broker_factory import AgentBrokerFactory  # pylint: disable=import-error


class Worker:
    def __init__(self):
        self.manager_factory = ManagerFactory()
        self.stack_manager = self.manager_factory.get_stack_manager()
        self.document_manager = self.manager_factory.get_document_manager()
        self.user_manager = self.manager_factory.get_user_manager()
        self.item_manager = self.manager_factory.get_item_manager()

        self.agent_broker_factory = AgentBrokerFactory()
        self.agent_broker = self.agent_broker_factory.get_agent_broker()
        self.thread_task_dict = {}

        self.hostname = get_hostname()

        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()
        self.task_broker.agent_broker = self.agent_broker

        signal_list = [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]
        logger.debug("[Worker] Adding signal handlers for {0}".format(signal_list))
        for sig in signal_list:
            signal.signal(sig, self.exit_handler)
        logger.debug("[Worker] Initialised Worker.")

    def run(self):
        try:
            logger.debug("[Worker] Starting Worker")
            time.sleep(5)
            self.task_broker.start_worker(subscribe_channels=self.get_subscribe_channels())

            logger.debug("[Worker] Starting queue listen")
            task_pop_thread = threading.Thread(target=self.start_task_popping, args=[])
            task_pop_thread.daemon = True  # ensures that this thread stops if worker stops
            task_pop_thread.start()

            kill = False
            while kill == False:
                time.sleep(10)
                if task_pop_thread.isAlive() == False:
                    logger.info("[Worker] task_pop_thread was found dead. Killing Worker.")
                    kill = True
                    break
        except Exception as e:
            logger.error("[Worker] Exception occured in Worker: {0}".format(e))

    def start_task_popping(self):
        logger.info("[Worker] start_task_popping. Starting listening on redis queue")
        while True:
            logger.info("[Worker] Waiting for items to appear in queue")
            tag = "common"
            task = self.task_broker.get_task(tag)

            logger.info("[Worker] Popped item. Type '{0}'. Item: '{1}'".format(type(task), task))

            task_attr = json.loads(task)  # TODO: do we pass tasks or do we pass dictionary?
            # logger.info("[Worker] Item as task_attr:  '{0}'. Type: '{1}'".format(task_attr, task_attr["topic"]))

            if task_attr["topic"] == "document_task":
                logger.info("[Worker] Document_Task with subtasks '{0}'".format(task_attr["subtasks"]))
                thread = threading.Thread(target=self.document_manager.handle_task, args=[task_attr])
                thread.start()
                continue
            elif task_attr["topic"] == "agent_task":
                logger.info("[Worker] Agent_Task with subtasks '{0}'".format(task_attr["subtasks"]))
                thread = threading.Thread(target=self.agent_broker.handle_task, args=[task_attr])
                thread.start()
                continue
            elif task_attr["topic"] == "stack_task":
                logger.info("[Worker] Stack_task with subtasks '{0}'".format(task_attr["subtasks"]))
                thread = threading.Thread(target=self.stack_manager.handle_task, args=[task_attr])
                thread.start()
                continue

    def get_subscribe_channels(self):
        return [
            'all',
            'worker',
            self.hostname
        ]

    def exit_handler(self, signum=None, frame=None):
        logger.info("[Worker] Signal handler called with signal {0}".format(str(signum)))
        logger.info(
            "[Worker] flushing queue")  # TODO: Is this still needed? Will we ever have tasks for specific workers so that they need to resubmit these tasks when they die?
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
