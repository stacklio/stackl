import logging

from stackl.enums.cast_type import CastType
from .handler import Handler
from stackl.tasks.result_task import ResultTask
from stackl.task_broker.task_broker_factory import TaskBrokerFactory

logger = logging.getLogger("STACKL_LOGGER")


class TaskHandler(Handler):
    def __init__(self):
        super(TaskHandler, self).__init__()

        logger.info(f"[TaskHandler] Starting TaskHandler.")
        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

    def handle(self, item):
        result = None
        if item.topic == 'report':
            pass
        elif item.topic == 'result':
            logger.info(
                f"[TaskHandler] Received result: {item.as_json_string()}. Processing."
            )
            self.task_broker.handle_result_task(item)
        else:
            logger.info(
                f"[TaskHandler] Unknown task with type '{item.topic}'! Ignoring."
            )
        if result is None:  #Keep for potential future use - in case we want report results
            return
        if item.get_attribute('return_channel'):
            return ResultTask({
                'channel': item.get_attribute('return_channel'),
                'cast_type': CastType.BROADCAST.value,
                'result': result,
                'source_task': item
            })
