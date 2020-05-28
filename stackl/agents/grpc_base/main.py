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
        (
            # Interval at which grpc will send keepalive pings
            'grpc.keepalive_time_ms',
            1000),
        (
            # Amount of time grpc waits for a keepalive ping to be
            # acknowledged before deeming the connection unhealthy and closing
            # this also sets TCP_USER_TIMEOUT for the underlying socket to this value
            'grpc.keepalive_timeout_ms',
            500)
    ]

    retries = 0
    while True:
        try:
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
                retries = 0
                for job in stub.GetJob(agent_metadata, wait_for_ready=True):
                    print("Job received from STACKL through gRPC stream")
                    job_handler.invoke_automation(job)
                    print("Waiting for new job")

        except (grpc._channel._Rendezvous,
                grpc._channel._InactiveRpcError) as e:
            print(f"Caught Rendezvous exception: {e}. Retry: {retries}")
            if retries > 10:
                raise RetriesExceeded(e)
            retries += 1
            time.sleep(5 * retries)
        except Exception as e:
            print(f"Exception during automation: {e}")
