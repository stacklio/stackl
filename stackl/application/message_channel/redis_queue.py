import logging
import socket
import threading
import time

from redis.sentinel import Sentinel

logger = logging.getLogger("STACKL_LOGGER")
from message_channel import MessageChannel
from task.task_factory import TaskFactory
from utils.general_utils import get_config_key


class RedisQueue(MessageChannel):

    def __init__(self):
        super(RedisQueue, self).__init__()

        self.queue = None
        self.pubsub = None
        self.task_handler = None

    def start(self, task_handler, subscribe_channels=[]):
        logger.info("[RedisQueue] Starting RedisQueue.")
        if self.started:
            logger.info("[RedisQueue] RedisQueue already started!")
        else:
            logger.info("[RedisQueue] RedisQueue connecting to redis")
            self.queue = self.RedisWrapper()
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
            self.queue = self.RedisWrapper()
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
            self.queue = self.RedisWrapper()
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

    # Inner class
    class RedisWrapper:
        def __init__(self):
            self.broker_is_sentinel_host = get_config_key('redisSentinelHost')

            logger.debug("[RedisWrapper] Configkey broker_is_sentinel_host: " + str(self.broker_is_sentinel_host))
            self.master = None
            self._get_sentinel()
            self._wait_redis()

        def exists(self, name):
            logger.debug("[RedisWrapper] Doing exists(). Name {0}".format(name))
            return self.get_master().exists(name)

        def pubsub_channels(self):
            logger.debug("[RedisWrapper] Doing pubsub_channels()")
            return self.get_slave().pubsub_channels()

        def pubsub(self):
            logger.debug("[RedisWrapper] Doing pubsub()")
            return self.get_master().pubsub()

        def publish(self, channel, message):
            logger.debug("[RedisWrapper] Doing publish(). channel {0} and message {1}".format(channel, message))
            return self.get_master().publish(channel, message)

        def delete(self, *names):
            logger.debug("[RedisWrapper] Doing delete(). Names {0}".format(*names))
            return self.get_master().delete(*names)

        def set(self, name, value):
            logger.debug("[RedisWrapper] Doing set(). Name {0} and value {1}".format(name, value))
            return self.get_master().set(name, value)

        def setnx(self, name, value):
            logger.debug("[RedisWrapper] Doing setnx(). Name {0} and value {1}".format(name, value))
            return self.get_master().setnx(name, value)

        def expire(self, name, time):
            logger.debug("[RedisWrapper] Doing expire(). Name {0} and time {1}".format(name, time))
            return self.get_master().expire(name, time)

        def rpush(self, name, *values):
            logger.debug("[RedisWrapper] Doing rpush(). Name {0} and values {1}".format(name, *values))
            return self.get_master().rpush(name, *values)

        def lpush(self, name, *values):
            logger.debug("[RedisWrapper] Doing lpush(). Name {0} and values {1}".format(name, *values))
            return self.get_master().lpush(name, *values)

        def lrange(self, name, start, stop):
            logger.debug(
                "[RedisWrapper] Doing lrange(). Name '{0}', start '{1}', stop '{2}'".format(name, start, stop))
            return self.get_slave().lrange(name, start, stop)

        def rpop(self, name):
            logger.debug("[RedisWrapper] Doing rpop(). Name '{0}'".format(name))
            return self.get_master().rpop(name)

        def block_rpop(self, name):
            logger.debug("[RedisWrapper] Doing block_rpop(). Name '{0}'".format(name))
            return self.get_master().brpop(name)

        def brpop(self, name):
            logger.debug("[RedisWrapper] Doing block_rpop(). Name '{0}'".format(name))
            return self.get_master().brpop(name)

        def setex(self, name, value, time):
            logger.debug(
                "[RedisWrapper] Doing setex(). Name '{0}', value '{1}' and time '{2}'".format(name, value, time))
            return self.get_master().setex(name, value, time)

        def scan_iter(self, match=None, count=None):
            logger.debug("[RedisWrapper] Doing scan_iter(). Match '{0}' and count '{1}'".format(match, count))
            return self.get_master().scan_iter(match, count)

        def get(self, name):
            return self.get_slave().get(name)

        def get_slave(self):
            try:
                logger.debug("[RedisWrapper] get_slave for 'mymaster'")
                slave = self.sentinel.slave_for('mymaster')
                slave.ping()
                return slave
            except Exception as e:
                logger.debug("[RedisWrapper] Exception occured while getting slave '{}' ".format(e))
                logger.debug("[RedisWrapper] Trying other sentinel...")
                self._get_sentinel()
                time.sleep(2)
            return self.get_slave()

        def get_master(self):
            try:
                if self.master:
                    # logger.debug("[RedisWrapper] get_master. There is a master. Ping.")
                    self.master.ping()
                    return self.master
                else:
                    logger.debug("[RedisWrapper] get_master. There isn't a master. calling _get_master_helper")
                    return self._get_master_helper()
            except Exception:
                logger.debug("[RedisWrapper] Exception in get_master: calling _get_master_helper")
                return self._get_master_helper()

        def _get_master_helper(self):
            while True:
                try:
                    self.master = self.sentinel.master_for('mymaster')
                    logger.debug("[RedisWrapper] Pinging master: '{0}', on address '{1}'".format(str(self.master),
                                                                                                 self.sentinel.discover_master(
                                                                                                     'mymaster')))
                    self.master.ping()
                    return self.master
                except Exception as e:
                    logger.debug("[RedisWrapper] Exception occured while getting master '{}' ".format(e))
                    logger.debug("[RedisWrapper] Trying other sentinel...")
                    self._get_sentinel()
                    time.sleep(2)

        def _get_sentinel(self):
            self.sentinel = Sentinel([(self.broker_is_sentinel_host, 26379)])

        def _wait_redis(self):
            logger.debug('[RedisWrapper] waiting for redis sentinel...')
            while True:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = s.connect_ex((self.broker_is_sentinel_host, 26379))
                    if result == 0:
                        logger.debug(
                            "[RedisWrapper] redis sentinel is listening... trying to invoke sentinel action to check if master is online")
                        s.close()
                        self.get_master()
                        break
                    else:
                        logger.debug("[RedisWrapper] waiting for connection...")
                except Exception as e:
                    logger.debug(
                        "[RedisWrapper] exception occured waiting for redis. Error: '{}'. Trying again.".format(e))
                time.sleep(5)
