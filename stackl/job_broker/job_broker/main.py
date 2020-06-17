import logging
from concurrent import futures

import grpc
from .automation_job_dispenser import AutomationJobDispenser
from stackl import stackl_globals
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl_protos.agent_pb2_grpc import add_StacklAgentServicer_to_server


def start():
    stackl_globals.initialize()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.keepalive_time_ms', 10000),
            # send keepalive ping every 10 second, default is 2 hours
            ('grpc.keepalive_timeout_ms', 5000),
            # keepalive ping time out after 5 seconds, default is 20 seoncds
            ('grpc.keepalive_permit_without_calls', True),
            # allow keepalive pings when there's no gRPC calls
            ('grpc.http2.max_pings_without_data', 0),
            # allow unlimited amount of keepalive pings without data
            ('grpc.http2.min_time_between_pings_ms', 10000),
            # allow grpc pings from client every 10 seconds
            ('grpc.http2.min_ping_interval_without_data_ms', 5000),
            # allow grpc pings from client without data every 5 seconds
        ])
    task_broker = TaskBrokerFactory().get_task_broker()
    add_StacklAgentServicer_to_server(
        AutomationJobDispenser(stackl_globals.redis_cache, task_broker),
        server)
    server.add_insecure_port('[::]:50051')
    print(
        "___________________ STARTING STACKL GRPC SERVER ____________________")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    start()
