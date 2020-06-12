import ast
import logging

from stackl.message_channel.message_channel_factory import MessageChannelFactory
from .task_broker import TaskBroker
from stackl.utils.general_utils import get_hostname

logger = logging.getLogger("STACKL_LOGGER")


class CustomTaskBroker(TaskBroker):
    def __init__(self):
        super().__init__()
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

    def start_worker(self, subscribe_channels=None):
        logger.debug(
            "[CustomTaskBroker] Starting CustomTaskBroker for Worker.")
        super().start_worker(subscribe_channels)
        self.message_channel.start(self.get_task_handler(), subscribe_channels)

    def get_task_handler(self):
        # Import here so this works with the rest component which doesn't have a taskhandler
        # might be worth to refactor this part
        from worker.handler.task_handler import TaskHandler
        return TaskHandler()

    def give_task(self, task_obj):
        super().give_task(task_obj)

        if getattr(task_obj, "topic", None) != "result":
            self.add_task_to_queue(task_obj)

        if task_obj.cast_type == "anycast":
            if getattr(task_obj, "return_channel", None) is None:
                task_obj.return_channel = get_hostname()
                logger.debug(
                    f"[CustomTaskBroker] give_task. Adding return_channel: '{task_obj.return_channel}'"
                )
            logger.debug(
                f"[CustomTaskBroker] give_task. Task to push: '{task_obj}'")
            self.message_channel.push("task_" + "common" + ':process',
                                      task_obj.as_json_string())
        else:
            self.message_channel.publish(task_obj)
        return

    def get_task_result(self, task_id):
        for result_task in self.message_channel.listen_result(get_hostname()):
            if task_id == ast.literal_eval(result_task.source_task)["id"]:
                return result_task

    def get_task(self, tag):
        task = self.message_channel.pop("task_" + tag + ':process')[1]
        logger.debug(f"[CustomTaskBroker] get_task. returning task: '{task}'")
        return task
