from stackl.utils.general_utils import get_config_key

from job_broker.message_channel.rabbit_mq_channel import RabbitMqChannel
from job_broker.message_channel.redis_channel import RedisChannel


def get_message_channel():
    message_channel_type = get_config_key('MESSAGE_CHANNEL')

    if message_channel_type == "RabbitMQ":
        return RabbitMqChannel()
    else:  # default to Redis
        return RedisChannel()