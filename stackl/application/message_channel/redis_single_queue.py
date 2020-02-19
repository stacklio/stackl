import logging
import threading
import time

from redis import StrictRedis

logger = logging.getLogger("STACKL_LOGGER")
from message_channel import MessageChannel
from task.task_factory import TaskFactory
from utils.general_utils import get_config_key


class RedisSingleQueue(MessageChannel):

    def __init__(self):
        super(RedisSingleQueue, self).__init__()
        self.redis_host = get_config_key("REDIS_HOST")

        self.queue = None
        self.pubsub = None
        self.task_handler = None

    def start(self, task_handler, subscribe_channels=[]):
        logger.info("[RedisQueue] Starting RedisQueue.")
        if self.started:
            logger.info("[RedisQueue] RedisQueue already started!")
        else:
            logger.info("[RedisQueue] RedisQueue connecting to redis")
            self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
            self.pubsub = self.queue.pubsub()
            if task_handler is None:
                raise Exception("[RedisQueue] Task handler must be set when starting Broker!")
            self.task_handler = task_handler
            self.start_pubsub(subscribe_channels)

    def start_pubsub(self, subscribe_channels):
        if len(subscribe_channels) > 0:
            logger.info("[RedisQueue] starting listening to subscribed channels: {0}".format(subscribe_channels))
            self.listen_management_thread = threading.Thread(target=self.listen_permanent, args=[subscribe_channels])
            self.listen_management_thread.daemon = True
            self.listen_management_thread.start()
        else:
            logger.info("[RedisQueue] postponing pubsub start due to empty channel list")

    def publish(self, task):
        return_channel = task.get_attribute('return_channel')
        wait_time = task.get_attribute('wait_time')
        channel = task.get_channel()
        message_str = task.as_json_string()
        logger.info(
            "[RedisQueue] Channel '{0}': Sending message via pubsub: {1}".format(str(channel), message_str))
        self.queue.publish(channel, message_str)
        if return_channel is not None:
            return self.listen(return_channel, wait_time=wait_time)
        return {}

    def listen_permanent(self, channels):
        try:
            self._pubsub_channels(self.pubsub, channels, action='subscribe')
            logger.info("[RedisQueue] Broker listening on: {0}".format(channels))
            self.started = True

            for message in self.pubsub.listen():
                logger.info("[RedisQueue] Broker got message: '{0}'".format(message))
                if message['type'] != 'subscribe':
                    # parse task
                    task = TaskFactory.create_task(message['data'])
                    result_task = self.task_handler.handle(task)
                    if result_task is not None and result_task.get_attribute('topic', '') == 'result':
                        time.sleep(0.5)
                        self.publish(result_task)

            logger.debug("[RedisQueue] Error listen_permanent stopped!")
            self._pubsub_channels(self.pubsub, channels, action='unsubscribe')
            raise Exception("[RedisQueue] Error listen_permanent stopped!")
        except Exception as e:
            logger.error("[RedisQueue] ERROR!!! EXCEPTION OCCURED IN listen_permanent: " + str(e))
            logger.error("[RedisQueue] Retrying to connect...")
            self.pubsub = self.queue.pubsub()
            self.listen_permanent(channels)

    def listen(self, channel, wait_time=5):
        logger.info("[RedisQueue] Listening temporary to channel " + str(channel))
        pubsub = self.queue.pubsub()
        self._pubsub_channels(pubsub, [channel], action='subscribe')
        return_array = []
        t_end = time.time() + wait_time
        while time.time() < t_end:
            message = pubsub.get_message()
            logger.info("[RedisQueue] Broker got message listen: " + str(message))
            if message and (message['type'] != 'subscribe' and message['type'] != 'unsubscribe'):
                result_task = TaskFactory.create_task(message['data'])
                logger.debug("[RedisQueue] resultTask: " + str(result_task.as_json_string()))
                return_array.append(result_task)
                continue
            time.sleep(0.1)
        self._pubsub_channels(pubsub, [channel], action='unsubscribe')
        logger.info("[RedisQueue] Broker listen returning: " + str(return_array))
        return return_array

    def push(self, name, *values):
        logger.debug("[RedisQueue] Doing push(). Name {0} and values {1}".format(name, *values))
        try:
            result = self.queue.lpush(name, *values)
        except Exception as e:
            logger.debug("[RedisQueue] Exception occured in push '{}'".format(e))
            logger.debug("[RedisQueue] Trying one more time with wait of 5 seconds")
            self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
            time.sleep(5)
            result = self.queue.lpush(name, *values)
        return result

    def pop(self, name):
        logger.debug("[RedisQueue] Doing pop(). Name {0}".format(name))
        try:
            result = self.queue.brpop(name)
        except Exception as e:
            logger.debug("[RedisQueue] Exception occured in pop '{}'".format(e))
            logger.debug("[RedisQueue] Trying one more time with wait of 5 seconds")
            self.queue = StrictRedis(host=self.redis_host, port=6379, db=0)
            time.sleep(5)
            result = self.queue.brpop(name)
        return result

    def _pubsub_channels(self, pubsub, channels, action='subscribe'):
        for channel in channels:
            if action == 'subscribe':
                logger.info("[RedisQueue] Subscribing to channel: " + str(channel))
                pubsub.subscribe(channel)
            if action == 'unsubscribe':
                logger.info("[RedisQueue] Unsubscribing to channel: " + str(channel))
                pubsub.unsubscribe(channel)
