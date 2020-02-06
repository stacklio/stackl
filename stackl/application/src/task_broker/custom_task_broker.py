from handler.task_handler import TaskHandler
from message_channel.message_channel_factory import MessageChannelFactory
from task_broker import TaskBroker
from utils.general_utils import get_hostname


class CustomTaskBroker(TaskBroker):

    def __init__(self):
        super().__init__('CustomTaskBroker')
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

    def start_stackl(self, subscribe_channels=[], agent_broker=None):
        super().start_stackl(subscribe_channels, agent_broker)
        self.logger.log("[CustomTaskBroker] Starting CustomTaskBroker for STACKL.")
        self.message_channel.start(self.get_task_handler(), subscribe_channels)

    def start_worker(self, subscribe_channels=[]):
        self.logger.log("[CustomTaskBroker] Starting CustomTaskBroker for Worker.")
        super().start_worker(subscribe_channels)
        self.message_channel.start(self.get_task_handler(), subscribe_channels)

    def get_task_handler(self):
        return TaskHandler('TaskHandler', self)

    def give_task(self, task_obj):
        try:
            super().give_task(task_obj)

            if getattr(task_obj, "topic", None) is not "result":
                self.add_task_to_queue(task_obj)

            if task_obj.cast_type is "anycast":
                if getattr(task_obj, "return_channel", None) is None:
                    task_obj.return_channel = get_hostname()
                    self.logger.log(
                        "[CustomTaskBroker] Task given. Added return_channel: '{0}'".format(task_obj.return_channel))
                if getattr(task_obj, "send_channel", None) is "agent":
                    task_obj.send_channel = self.agent_broker.get_agent_for_task(task_obj)
                    self.logger.log(
                        "[CustomTaskBroker] Task given. Added send_channel: '{0}'".format(task_obj.send_channel))

                self.logger.log(
                    "[CustomTaskBroker] Task given. Added return_channel: '{0}'".format(task_obj.return_channel))
                self.message_channel.push("task_" + "common" + ':process', task_obj.as_json_string())
            else:
                self.message_channel.publish(task_obj)
        except Exception as e:
            self.logger.error("[CustomTaskBroker] Invalid task received. Error message '{0}'", e)

    def get_task(self, tag):
        task = self.message_channel.pop("task_" + tag + ':process')[1]
        self.logger.log("[CustomTaskBroker] get_task. returning task: '{0}'".format(task))
        return task
