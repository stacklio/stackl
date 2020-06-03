import os
import grpc
import time
from protos.agent_pb2 import AgentMetadata, AutomationResult, Status
from protos.agent_pb2_grpc import StacklAgentStub
from tool_factory import ToolFactory


class RetriesExceeded(Exception):
    """docstring for RetriesExceeded"""
    pass


class JobHandler:
    def __init__(self, stackl_agent_stub):
        self.tool_factory = ToolFactory()
        self.stackl_agent_stub = stackl_agent_stub

    def invoke_automation(self, invoc):
        handler = self.tool_factory.get_handler(invoc)
        result, error_message = handler.handle()
        print("Handle done")
        print(result)
        print(error_message)
        automation_result = AutomationResult()
        automation_result.stack_instance = invoc.stack_instance
        automation_result.service = invoc.service
        automation_result.functional_requirement = invoc.functional_requirement
        automation_result.infrastructure_target = invoc.infrastructure_target
        if result == 0:
            automation_result.status = Status.READY
        else:
            automation_result.status = Status.FAILED
            automation_result.error_message = error_message

        print("Handle done")
        response = self.stackl_agent_stub.ReportResult(automation_result)
        print(response)


if __name__ == '__main__':
    print(
        f'starting {os.environ["AGENT_NAME"]} agent to {os.environ["STACKL_GRPC_HOST"]}'
    )
    channel_opts = [
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
        ('grpc.http2.min_ping_interval_without_data_ms',  5000),
        # allow grpc pings from client without data every 5 seconds
    ]

    with grpc.insecure_channel(f"{os.environ['STACKL_GRPC_HOST']}",
                               options=channel_opts) as channel:
        stub = StacklAgentStub(grpc.intercept_channel(channel))
        agent_metadata = AgentMetadata()
        agent_metadata.name = os.environ["AGENT_ID"]
        agent_metadata.selector = os.environ["AGENT_SELECTOR"]
        response = stub.RegisterAgent(agent_metadata)
        job_handler = JobHandler(stub)
        if not response.success:
            exit(0)
        print(
            f'Connected to STACKL with gRPC at {os.environ["STACKL_GRPC_HOST"]}'
        )
        for job in stub.GetJob(agent_metadata, wait_for_ready=True):
            print("Job received from STACKL through gRPC stream")
            try:
                job_handler.invoke_automation(job)
                print("Waiting for new job")
            except Exception as e:
                print(f"Exception during automation: {e}")
