from concurrent import futures

import grpc

import protos.agent_pb2_grpc
from handlers.tool_factory import ToolFactory
from protos.agent_pb2 import AutomationResponse


class StacklAgentServicer(protos.agent_pb2_grpc.StacklAgentServicer):

    def __init__(self):
        self.tool_factory = ToolFactory()

    def InvokeAutomation(self, request, context):
        print(request)
        automation_response = protos.agent_pb2.AutomationResponse()
        for invoc in request.invocation:
            handler = self.tool_factory.get_handler(invoc.tool)
            automation_result = automation_response.automation_result.add()
            result, error_message = handler.handle(invoc, request.action)
            automation_result.service = invoc.service
            automation_result.functional_requirement = invoc.functional_requirement
            if result == 0:
                automation_result.status = protos.agent_pb2.AutomationResponse.Status.READY
            else:
                automation_result.status = protos.agent_pb2.AutomationResponse.Status.FAILED
            automation_result.error_message = error_message
        return automation_response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protos.agent_pb2_grpc.add_StacklAgentServicer_to_server(
        StacklAgentServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    print("starting docker agent")
    serve()
