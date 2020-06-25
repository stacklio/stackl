import logging

from stackl.message_channel.message_channel_factory import MessageChannelFactory
from stackl.utils.general_utils import get_hostname

from .task_broker import TaskBroker

logger = logging.getLogger("STACKL_LOGGER")


class CustomTaskBroker(TaskBroker):
    def __init__(self):
        super().__init__()
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

    def give_task(self, task_obj):
        if task_obj.topic != "result":
            self.add_task_to_queue(task_obj)

        if task_obj.cast_type == "anycast":
            if getattr(task_obj, "return_channel", None) is None:
                task_obj.return_channel = get_hostname()
                logger.debug(
                    f"[CustomTaskBroker] give_task. Adding return_channel: '{task_obj.return_channel}'"
                )
            logger.debug(
                f"[CustomTaskBroker] give_task. Task to push: '{task_obj}'")
            self.message_channel.push("task_common", task_obj.json())
        else:
            self.message_channel.publish(task_obj)
        return

    def get_task_result(self, task_id):
        for result_task in self.message_channel.listen_result(get_hostname()):
            if task_id == result_task.source_task.id:
                return result_task

    def get_task(self, tag):
        task = self.message_channel.pop("task_" + tag)[1]
        logger.debug(f"[CustomTaskBroker] get_task. returning task: '{task}'")
        return task
