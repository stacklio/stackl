import os

import grpc

from protos.agent_pb2 import AgentMetadata, AutomationResult, Status
from protos.agent_pb2_grpc import StacklAgentStub
from tool_factory import ToolFactory


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
    channel = grpc.insecure_channel(f"{os.environ['STACKL_GRPC_HOST']}")
    stub = StacklAgentStub(channel)
    agent_metadata = AgentMetadata()
    agent_metadata.name = os.environ["AGENT_ID"]
    agent_metadata.selector = os.environ["AGENT_SELECTOR"]
    response = stub.RegisterAgent(agent_metadata)
    job_handler = JobHandler(stub)
    if not response.success:
        exit(0)
    print("Connected")
    for job in stub.GetJob(agent_metadata):
        print("job")
        try:
            job_handler.invoke_automation(job)
            print("Waiting for new job")
        except Exception:
            print("Catching everything cause we dont want this to crash")
