import logging

from stackl.task_broker.custom_task_broker import CustomTaskBroker
from stackl.utils.general_utils import get_config_key
from stackl.utils.stackl_singleton import Singleton

logger = logging.getLogger("STACKL_LOGGER")


class TaskBrokerFactory(metaclass=Singleton):
    def __init__(self):
        self.task_broker_type = get_config_key("TASK_BROKER")

        logger.info(
            f"[TaskBrokerFactory] Creating Task Broker with type: {self.task_broker_type}"
        )
        if self.task_broker_type == "Custom":
            self.task_broker = CustomTaskBroker()
        else:  # assume local custom redis broker
            self.task_broker = CustomTaskBroker()

    def get_task_broker(self):
        return self.task_broker
