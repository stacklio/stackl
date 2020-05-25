import os
import abc
import grpc
import logging
import time
from random import randint
from protos.agent_pb2 import AgentMetadata, AutomationResult, Status
from protos.agent_pb2_grpc import StacklAgentStub
from tool_factory import ToolFactory

class SleepingPolicy(abc.ABC):
    @abc.abstractmethod
    def sleep(self, try_i: int):
        """
        How long to sleep in milliseconds.
        :param try_i: the number of retry (starting from zero)
        """
        assert try_i >= 0

class ExponentialBackoff(SleepingPolicy):
    def __init__(self, *, init_backoff_ms: int, max_backoff_ms: int, multiplier: int):
        self.init_backoff = randint(0, init_backoff_ms)
        self.max_backoff = max_backoff_ms
        self.multiplier = multiplier

    def sleep(self, try_i: int):
        sleep_range = min(
            self.init_backoff * self.multiplier ** try_i, self.max_backoff
        )
        sleep_ms = randint(0, sleep_range)
        logging.debug(f"Sleeping for {sleep_ms}")
        time.sleep(sleep_ms / 1000)

# class RetryOnRpcErrorClientInterceptor(
#     grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor
# ):
#     def __init__(
#         self,
#         *,
#         max_attempts: int,
#         sleeping_policy: SleepingPolicy,
#         status_for_retry: Optional[Tuple[grpc.StatusCode]] = None,
#     ):
#         self.max_attempts = max_attempts
#         self.sleeping_policy = sleeping_policy
#         self.status_for_retry = status_for_retry

#     def _intercept_call(self, continuation, client_call_details, request_or_iterator):

#         for try_i in range(self.max_attempts):
#             response = continuation(client_call_details, request_or_iterator)

#             if isinstance(response, grpc.RpcError):

#                 # Return if it was last attempt
#                 if try_i == (self.max_attempts - 1):
#                     return response

#                 # If status code is not in retryable status codes
#                 if (
#                     self.status_for_retry
#                     and response.code() not in self.status_for_retry
#                 ):
#                     return response

#                 self.sleeping_policy.sleep(try_i)
#             else:
#                 return response

#     def intercept_unary_unary(self, continuation, client_call_details, request):
#         return self._intercept_call(continuation, client_call_details, request)

#     def intercept_stream_unary(
#         self, continuation, client_call_details, request_iterator
#     ):
#         return self._intercept_call(continuation, client_call_details, request_iterator)

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
            1000
        ),
        (
            # Amount of time grpc waits for a keepalive ping to be 
            # acknowledged before deeming the connection unhealthy and closing
            # this also sets TCP_USER_TIMEOUT for the underlying socket to this value
            'grpc.keepalive_timeout_ms',
            500
        )
    ]
    
    # with grpc.secure_channel(f"{os.environ['STACKL_GRPC_HOST']}", options=channel_opts) as channel:
    with grpc.insecure_channel(f"{os.environ['STACKL_GRPC_HOST']}", options=channel_opts) as channel:
        # interceptors = (
        #     RetryOnRpcErrorClientInterceptor(
        #         max_attempts=4,
        #         sleeping_policy=ExponentialBackoff(init_backoff_ms=100, max_backoff_ms=1600, multiplier=2),
        #         status_for_retry=(grpc.StatusCode.UNAVAILABLE,),
        #     ),
        # )
        # stub = StacklAgentStub(grpc.intercept_channel(channel, *interceptors))
        stub = StacklAgentStub(grpc.intercept_channel(channel))
        agent_metadata = AgentMetadata()
        agent_metadata.name = os.environ["AGENT_ID"]
        agent_metadata.selector = os.environ["AGENT_SELECTOR"]
        response = stub.RegisterAgent(agent_metadata)
        job_handler = JobHandler(stub)
        if not response.success:
            exit(0)
        print(f'Connected to STACKL with gRPC at {os.environ["STACKL_GRPC_HOST"]}')
        for job in stub.GetJob(agent_metadata, wait_for_ready=True):
            print("Job received from STACKL through gRPC stream")
            try:
                job_handler.invoke_automation(job)
                print("Waiting for new job")
            except Exception as e:
                print(
                    f"Exception during automation: {e}"
                )
