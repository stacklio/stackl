import logging

from enums.cast_type import CastType
from handler import Handler
from task.result_task import ResultTask
from task_broker.task_broker_factory import TaskBrokerFactory

logger = logging.getLogger("STACKL_LOGGER")

##TODO at the moment this class is sparse but it will be necessary for rollback and failure mechanisms
class TaskHandler(Handler):

    def __init__(self, stackl_type, call_object):
        super(TaskHandler, self).__init__(None)

        self.call_object = call_object
        self.stackl_type = stackl_type
        logger.info(
            "[TaskHandler] Created with stackl_type '{0}' and call_object '{1}'".format(stackl_type, call_object))
        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

    def handle(self, task):
        result = None
        if task.topic == 'report':  # TODO This is old stackl terminology, independent of OPA Queries
            if task.get_attribute('function'):
                result = getattr(self.call_object, task.get_attribute('function'))(*task.get_attribute('args'))
            else:
                result = getattr(self.call_object, task.get_attribute('attribute'))
        elif task.topic == 'ping':  # TODO Future potential task 
            logger.info("[TaskHandler] Received ping: " + str(task.as_json_string()))
            result = {'reply': 'pong', "type": self.stackl_type}
        elif task.topic == 'result':
            logger.info("[TaskHandler] Received result (as json_string): " + str(task.as_json_string()))
            logger.info("[TaskHandler] asking broker '{0}' to remove it from queue".format(self.task_broker))
            self.task_broker.remove_task_from_queue(task)
        else:
            logger.info("[TaskHandler] Unknown task with type '{0}'! Ignoring.".format(task.topic))
        if result is None:
            return
        if task.get_attribute('return_channel'):
            return ResultTask({
                'channel': task.get_attribute('return_channel'),
                'cast_type': CastType.BROADCAST.value,
                'result': result,
                'source_task': task
            })
