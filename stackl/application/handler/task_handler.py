import logging

from enums.cast_type import CastType
from handler import Handler
from task.result_task import ResultTask
from task_broker.task_broker_factory import TaskBrokerFactory

logger = logging.getLogger("STACKL_LOGGER")


# TODO at the moment this class is sparse but it will be necessary for rollback and failure mechanisms
class TaskHandler(Handler):
    def __init__(self, stackl_type, call_object):
        super(TaskHandler, self).__init__()

        self.call_object = call_object
        self.stackl_type = stackl_type
        logger.info(
            f"[TaskHandler] Created with stackl_type {stackl_type}' and call_object '{call_object}'"
        )
        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

    def handle(self, task):  #pylint: disable=arguments-differ
        result = None
        if task.topic == 'report':
            if task.get_attribute('function'):
                result = getattr(self.call_object,
                                 task.get_attribute('function'))(
                                     *task.get_attribute('args'))
            else:
                result = getattr(self.call_object,
                                 task.get_attribute('attribute'))
        elif task.topic == 'result':
            logger.info(
                f"[TaskHandler] Received result: {task.as_json_string()}. Processing."
            )
            self.task_broker.handle_result_task(task)
        else:
            logger.info(
                "[TaskHandler] Unknown task with type '{task.topic}'! Ignoring."
            )
        if result is None:
            return
        if task.get_attribute('return_channel'):
            return ResultTask({
                'channel': task.get_attribute('return_channel'),
                'cast_type': CastType.BROADCAST.value,
                'result': result,
                'source_task': task
            })
