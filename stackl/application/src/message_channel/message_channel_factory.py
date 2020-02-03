import sys



from logger import Logger
from utils.stackl_singleton import Singleton
from utils.general_utils import get_config_key

class MessageChannelFactory(metaclass=Singleton):

    def __init__(self):
        self.message_channel_type = get_config_key('MESSAGE_CHANNEL')
        self.logger = Logger("MessageChannelFactory")
        self.logger.info("[MessageChannelFactory] Creating Message Channel with type: {}".format(self.message_channel_type))
        self.message_channel = None
        
        if self.message_channel_type == "Redis":
            from message_channel.redis_queue import RedisQueue
            self.message_channel = RedisQueue()
        if self.message_channel_type == "RedisSingle":
            from message_channel.redis_single_queue import RedisSingleQueue
            self.message_channel = RedisSingleQueue()
        else: #default Redis
            from message_channel.redis_queue import RedisQueue
            self.message_channel = RedisQueue()

    def get_message_channel(self):
        self.logger.info("[MessageChannelFactory] Giving message channel with type '{0}' and id '{1}'".format(self.message_channel_type, self.message_channel))
        return self.message_channel