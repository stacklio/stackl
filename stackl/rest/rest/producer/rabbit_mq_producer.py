import pika
from stackl.tasks.task import Task

from rest.producer.producer import Producer
from stackl.tasks.result_task import ResultTask


class RabbitMqProducer(Producer):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=False)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue,
                                   on_message_callback=self.on_response,
                                   auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def give_task_and_get_result(self, task: Task) -> ResultTask:
        self.response = None
        self.corr_id = task.id
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id),
                                   body=task.json())
        while self.response is None:
            self.connection.process_data_events()
        return ResultTask.parse_raw(self.response)
