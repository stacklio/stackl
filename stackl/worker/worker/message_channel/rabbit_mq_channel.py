import json

import pika
from stackl.tasks.agent_task import AgentTask
from stackl.tasks.document_task import DocumentTask
from stackl.tasks.report_task import ReportTask
from stackl.tasks.result_task import ResultTask
from stackl.tasks.snapshot_task import SnapshotTask
from stackl.tasks.stack_task import StackTask

from .message_channel import MessageChannel


class RabbitMqChannel(MessageChannel):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='rpc_queue',
                                   on_message_callback=self.on_request)

    def on_request(self, ch, method, props, body):
        task_dict = {
            "document_task": DocumentTask,
            "agent_task": AgentTask,
            "report_task": ReportTask,
            "result_task": ResultTask,
            "snapshot_task": SnapshotTask,
            "stack_task": StackTask
        }
        task_json = json.loads(body)

        task = task_dict[task_json["topic"]].parse_obj(task_json)
        result_task = self.process_task_function(task)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                             correlation_id=props.correlation_id),
                         body=result_task.json())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_agent_task(self, task, channel_name, selector=""):
        channel = self.connection.channel()
        channel.basic_publish(exchange=channel_name,
                              routing_key=selector,
                              body=task.json())

    def start(self, process_function):
        self.process_task_function = process_function
        self.channel.start_consuming()
