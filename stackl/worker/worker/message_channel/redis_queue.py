import json
import logging

from redis import StrictRedis
from stackl.tasks.result_task import ResultTask
from stackl.utils.general_utils import get_config_key

from .message_channel import MessageChannel

logger = logging.getLogger("STACKL_LOGGER")


class RedisQueue(MessageChannel):
    def __init__(self):
        super(RedisQueue, self).__init__()
        self.redis_host = get_config_key("REDIS_HOST")

        self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
        self.pubsub = None
        self.task_handler = None
        self.listen_management_thread = None

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
                task = json.loads(message['data'])
                if task["topic"] == "result":
                    yield ResultTask.parse_obj(task)

    def push(self, name, *values):
        logger.debug(
            f"[RedisQueue] Doing push(). Name {name} and values {values}")
        result = self.queue.lpush(name, *values)
        return result

    def pop(self, name):
        logger.debug(f"[RedisQueue] Doing pop(). Name {name}")
        return self.queue.brpop(name)

    def _pubsub_channels(self, pubsub, channels, action='subscribe'):
        for channel in channels:
            if action == 'subscribe':
                logger.info(f"[RedisQueue] Subscribing to channel: {channel}")
                pubsub.subscribe(channel)
            if action == 'unsubscribe':
                logger.info(
                    f"[RedisQueue] Unsubscribing to channel: {channel}")
                pubsub.unsubscribe(channel)
