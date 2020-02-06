import grpc

import protos.agent_pb2
import protos.agent_pb2_grpc
from agent_broker import AgentBroker
from logger import Logger
from model.items.functional_requirement_status import FunctionalRequirementStatus, Status
from utils.general_utils import get_config_key


class GrpcAgentBroker(AgentBroker):

    def __init__(self):
        super(GrpcAgentBroker, self).__init__()
        self.logger = Logger("GrpcAgentBroker")
        stackl_agent = get_config_key("AGENT_HOST")
        self.channel = grpc.insecure_channel(str(stackl_agent))
        self.stub = protos.agent_pb2_grpc.StacklAgentStub(self.channel)

    def start(self):
        self.logger.info("[GrpcAgentBroker] Starting GrpcAgentBroker")

    def get_agent_for_task(self, task):
        return "gRPC"

    def send_to_agent(self, agent_connect_info, obj):
        self.logger.info("[GrpcAgentBroker] sending automation message to channel {0}".format(self.channel))
        self.logger.info("[GrpcAgentBroker] sending message: {0}".format(obj.SerializeToString()))
        result = self.stub.InvokeAutomation(obj)
        self.logger.info("[GrpcAgentBroker] received result: {0}".format(result))
        return result

    def process_result(self, stack_instance, result, document_manager):
        self.logger.info("[GrpcAgentBroker] processing result: {0}".format(result))
        for sts in result.automation_result:
            stack_instance.services[sts.service].status = []
        for sts in result.automation_result:
            self.logger.info("[GrpcAgentBroker] check sts: {0}".format(sts))
            fr_status = FunctionalRequirementStatus()
            fr_status.functional_requirement = sts.functional_requirement
            if sts.error_message == "":
                fr_status.status = Status.ready
            else:
                fr_status.status = Status.failed
                fr_status.error_message = sts.error_message
            stack_instance.services[sts.service].status.append(fr_status)
        document_manager.write_stack_instance(stack_instance)

    def create_change_obj(self, stack_instance, action, document_manager):
        self.logger.log(
            "[GrpcAgentBroker] create_change_obj. For stack_instance '{0}' and action '{1}'".format(stack_instance,
                                                                                                    action))
        change_obj = protos.agent_pb2.AutomationMessage()
        change_obj.action = action
        for service in stack_instance.services:
            service_name = service
            self.logger.log("[GrpcAgentBroker] service name: '{0}".format(service_name))
            service_doc = document_manager.get_document(type="service", document_name=service_name)
            self.logger.log("[GrpcAgentBroker] service doc: '{0}".format(service_doc))
            for fr in service_doc["functional_requirements"]:
                fr_doc = document_manager.get_document(type="functional_requirement", document_name=fr)
                self.logger.log(
                    "[GrpcAgentBroker] create_change_obj. Retrieved fr '{0}' from service_doc '{1}''".format(fr_doc,
                                                                                                             service_doc))
                invoc = change_obj.invocation.add()
                invoc.functional_requirement = fr
                invoc.image = fr_doc['invocation']['image']
                self.logger.log("[GrpcAgentBroker] create_change_obj. service debug '{0}'".format(
                    stack_instance.services[service_name]))
                invoc.infrastructure_target = stack_instance.services[service_name].infrastructure_target
                invoc.stack_instance = stack_instance.name
                invoc.tool = fr_doc['invocation']['tool']
                invoc.service = service_name
                self.logger.log(
                    "[GrpcAgentBroker] create_change_obj. Added fr '{0}' and invoc '{1}' to change_obj '{2}'"
                        .format(fr_doc, invoc.SerializeToString(), change_obj.SerializeToString()))
        return change_obj
