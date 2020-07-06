from rest.producer.producer import Producer
from rest.producer.rabbit_mq_producer import RabbitMqProducer


def get_producer() -> Producer:
    return RabbitMqProducer()
