import pika
from stackl.tasks.agent_task import AgentTask
from stackl.utils.general_utils import get_config_key

from job_broker.message_channel.message_channel import MessageChannel
from stackl.tasks.task import Task

from stackl.tasks.result_task import ResultTask


class RabbitMqChannel(MessageChannel):
    def __init__(self):
        self.rabbit_host = get_config_key("RABBIT_HOST", "localhost")
        self.rabbit_port = get_config_key("RABBIT_PORT", 5672)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host,
                                      port=self.rabbit_port))

        self.rpc_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host,
                                      port=self.rabbit_port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='stackl_jobs',
                                      exchange_type='topic')
        result = self.channel.queue_declare('stackl_jobs', exclusive=True)
        self.queue_name = result.method.queue

    def register_agent(self, name, selector):
        self.channel.queue_bind(exchange='stackl_jobs',
                                queue=self.queue_name,
                                routing_key=selector)

    # With RabbitMQ we don't need to delete the queue, as soon as an agent can pick it up it will
    def unregister_agent(self):
        pass

    def listen_for_jobs(self, callback_function):
        for method, properties, body in self.channel.consume(
                queue=self.queue_name, auto_ack=True):
            agent_task = AgentTask.parse_raw(body)
            yield callback_function(agent_task)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def give_task_and_get_result(self, task: Task) -> ResultTask:
        self.response = None
        self.corr_id = task.id

        channel = self.rpc_connection.channel()
        result = channel.queue_declare('', exclusive=False)
        queue_name = result.method.queue
        channel.basic_consume(queue=queue_name,
                              on_message_callback=self.on_response,
                              auto_ack=True)
        channel.basic_publish(exchange='',
                              routing_key='rpc_queue',
                              properties=pika.BasicProperties(
                                  reply_to=queue_name,
                                  correlation_id=self.corr_id),
                              body=task.json())
        while self.response is None:
            self.rpc_connection.process_data_events()
        return ResultTask.parse_raw(self.response)
