import logging

from utils.general_utils import get_config_key
from utils.stackl_singleton import Singleton


logger = logging.getLogger("STACKL_LOGGER")


class TaskBrokerFactory(metaclass=Singleton):
    def __init__(self):
        self.task_broker_type = get_config_key("TASK_BROKER")

        logger.info(
            f"[TaskBrokerFactory] Creating Task Broker with type: {self.task_broker_type}"
        )
        self.task_broker = None
        if self.task_broker_type == "Custom":
            from task_broker.custom_task_broker import CustomTaskBroker
            self.task_broker = CustomTaskBroker()
        else:  # assume local custom redis broker
            from task_broker.custom_task_broker import CustomTaskBroker
            self.task_broker = CustomTaskBroker()

    def get_task_broker(self):
        return self.task_broker
