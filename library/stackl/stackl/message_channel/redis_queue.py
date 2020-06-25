import logging
import threading
import time
from redis import StrictRedis

from .message_channel import MessageChannel
from stackl.tasks.task_factory import TaskFactory
from stackl.utils.general_utils import get_config_key

from ..tasks.result_task import ResultTask

logger = logging.getLogger("STACKL_LOGGER")


class RedisQueue(MessageChannel):
    def __init__(self):
        super(RedisQueue, self).__init__()
        self.redis_host = get_config_key("REDIS_HOST")

        self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
        self.pubsub = None
        self.task_handler = None
        self.listen_management_thread = None

    def start(self, task_handler, subscribe_channels):
        logger.info("[RedisQueue] Starting RedisQueue.")
        if self.started:
            logger.info("[RedisQueue] RedisQueue already started!")
        else:
            logger.info("[RedisQueue] RedisQueue connecting to redis")
            self.pubsub = self.queue.pubsub()
            if task_handler is None:
                raise Exception(
                    "[RedisQueue] Task handler must be set when starting Broker!"
                )
            self.task_handler = task_handler
            self.start_pubsub(subscribe_channels)

    def start_pubsub(self, subscribe_channels):
        if len(subscribe_channels) > 0:
            logger.info(
                f"[RedisQueue] start listen to subscribed channels: {subscribe_channels}"
            )
            self.listen_management_thread = threading.Thread(
                target=self.listen_permanent, args=[subscribe_channels])
            self.listen_management_thread.daemon = True
            self.listen_management_thread.start()
        else:
            logger.info(
                "[RedisQueue] postpone pubsub start due to empty channel list")

    def publish(self, task):
        channel = task.channel
        message_str = task.json()
        logger.info(
            f"[RedisQueue] Channel '{channel}': Sending message via pubsub: {message_str}"
        )
        self.queue.publish(channel, message_str)

    def listen_result(self, channel):
        logger.info(f"[RedisQueue] Broker listening on: {channel}")
        psub = self.queue.pubsub()
        psub.subscribe(channel)
        for message in psub.listen():
            logger.info(f"[RedisQueue] Broker got message: '{message}'")
            if message['type'] != 'subscribe':
                task = TaskFactory.create_task(message['data'])
                if isinstance(task, ResultTask):
                    yield task

    def listen_permanent(self, channels):
        self._pubsub_channels(self.pubsub, channels, action='subscribe')
        logger.info(f"[RedisQueue] Broker listening on: {channels}")
        self.started = True

        for message in self.pubsub.listen():
            logger.info(f"[RedisQueue] Broker got message: '{message}'")
            if message['type'] != 'subscribe':
                # parse task
                task = TaskFactory.create_task(message['data'])
                result_task = self.task_handler.handle(task)
                if result_task is not None and result_task.get_attribute(
                        'topic', '') == 'result':
                    time.sleep(0.5)
                    self.publish(result_task)

        logger.debug("[RedisQueue] Error listen_permanent stopped")
        self._pubsub_channels(self.pubsub, channels, action='unsubscribe')

    def listen(self, channel, timeout=5):
        logger.info(f"[RedisQueue] Listening temporary to channel {channel}")
        pubsub = self.queue.pubsub()
        self._pubsub_channels(pubsub, [channel], action='subscribe')
        return_array = []
        t_end = time.time() + timeout
        while time.time() < t_end:
            message = pubsub.get_message()
            logger.info(f"[RedisQueue] Broker got message listen: {message}")
            if message and (message['type'] != 'subscribe'
                            and message['type'] != 'unsubscribe'):
                result_task = TaskFactory.create_task(message['data'])
                logger.debug(f"[RedisQueue] resultTask: {result_task.json()}")
                return_array.append(result_task)
                continue
            time.sleep(0.1)
        self._pubsub_channels(pubsub, [channel], action='unsubscribe')
        logger.info(f"[RedisQueue] Broker listen returning: {return_array}")
        return return_array

    def push(self, name, *values):
        logger.debug(
            f"[RedisQueue] Doing push(). Name {name} and values {values}")
        result = self.queue.lpush(name, *values)
        return result

    def pop(self, name):
        logger.debug(f"[RedisQueue] Doing pop(). Name {name}")
        try:
            result = self.queue.brpop(name)
        except Exception as e:  #pylint: disable=broad-except
            logger.debug(f"[RedisQueue] Exception occured in pop '{e}'")
            logger.debug("[RedisQueue] Trying again with wait of 5 seconds")
            self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
            time.sleep(5)
            result = self.queue.brpop(name)
        return result

    def _pubsub_channels(self, pubsub, channels, action='subscribe'):
        for channel in channels:
            if action == 'subscribe':
                logger.info(f"[RedisQueue] Subscribing to channel: {channel}")
                pubsub.subscribe(channel)
            if action == 'unsubscribe':
                logger.info(
                    f"[RedisQueue] Unsubscribing to channel: {channel}")
                pubsub.unsubscribe(channel)
