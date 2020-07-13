import logging.config
import os

from core.message_channel.message_channel_factory import MessageChannelFactory
from stackl.tasks.task import Task
from stackl.utils.general_utils import get_hostname  # pylint: disable=import-error

from core.manager import ManagerFactory  # pylint: disable=no-name-in-module,import-error

# initialize stackl globals

from loguru import logger
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
        message_channel_factory = MessageChannelFactory()
        self.stack_manager = self.manager_factory.get_stack_manager()
        self.document_manager = self.manager_factory.get_document_manager()
        self.snapshot_manager = self.manager_factory.get_snapshot_manager()

        self.hostname = get_hostname()

        self.message_channel = message_channel_factory.get_message_channel()

        logger.debug("[Worker] Initialised Worker.")

    def run(self):
        logger.debug("[Worker] Starting Worker")
        self.message_channel.start(self.process_task)

    def process_task(self, task: Task):
        if task.topic == "document_task":
            return self.document_manager.handle_task(task)
        elif task.topic == "snapshot_task":
            return self.snapshot_manager.handle_task(task)
        elif task.topic == "stack_task":
            return self.stack_manager.handle_task(task)

    def get_subscribe_channels(self):
        return ['all', 'worker', self.hostname]


def start():
    worker = Worker()
    worker.run()


if __name__ == '__main__':
    start()
