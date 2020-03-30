import logging

import grpc

import protos.agent_pb2
import protos.agent_pb2_grpc
from agent_broker import AgentBroker
from model.items.functional_requirement_status_model import FunctionalRequirementStatus, Status
from utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")

class GrpcAgentBroker(AgentBroker):

    def __init__(self):
        super(GrpcAgentBroker, self).__init__()

        stackl_agent = get_config_key("AGENT_HOST")
        self.channel = grpc.insecure_channel(str(stackl_agent))
        self.stub = protos.agent_pb2_grpc.StacklAgentStub(self.channel)

    def start(self):
        logger.info("[GrpcAgentBroker] Starting GrpcAgentBroker")

    def get_agent_for_task(self, task):
        return "gRPC"

    def send_job_to_agent(self, agent_connect_info, job):
        logger.info("[GrpcAgentBroker] sending automation message to channel {0}".format(self.channel))
        result = self.stub.InvokeAutomation(job)
        # logger.info("[GrpcAgentBroker] received result: {0}".format(result))
        return result

    def process_job_result(self, stack_instance, result, document_manager):
        logger.info("[GrpcAgentBroker] processing result: {0}".format(result))
        sts = result.automation_result
        stack_instance.services[sts.service].status = []

        logger.info("[GrpcAgentBroker] check sts: {0}".format(sts))

        if sts.error_message == "":
            status = Status.ready
        else:
            status = Status.failed
        fr_status = FunctionalRequirementStatus(
            functional_requirement=sts.functional_requirement,
            status=status,
            error_message=sts.error_message
        )
        stack_instance.services[sts.service].status.append(fr_status)
        if len(sts.hosts) > 0:
            stack_instance.services[sts.service].hosts = []
            for h in sts.hosts:
                stack_instance.services[sts.service].hosts.append(h)
        document_manager.write_stack_instance(stack_instance)

    def create_job_for_agent(self, stack_instance, action, document_manager):
        logger.debug(
            "[GrpcAgentBroker] create_job_for_agent. For stack_instance '{0}' and action '{1}'".format(stack_instance, action))
        job = []
        for service in stack_instance.services:
            service_name = service
            logger.debug("[GrpcAgentBroker] service name: '{0}".format(service_name))
            service_doc = document_manager.get_document(type="service", document_name=service_name)
            logger.debug("[GrpcAgentBroker] service doc: '{0}".format(service_doc))
            for fr in service_doc["functional_requirements"]:
                fr_doc = document_manager.get_document(type="functional_requirement", document_name=fr)
                logger.debug(
                    "[GrpcAgentBroker] create_job_for_agent. Retrieved fr '{0}' from service_doc '{1}''".format(fr_doc,
                                                                                                           service_doc))
                automation_message = protos.agent_pb2.AutomationMessage()
                automation_message.action = action
                invoc = automation_message.invocation
                invoc.functional_requirement = fr
                invoc.image = fr_doc['invocation']['image']
                logger.debug("[GrpcAgentBroker] create_job_for_agent. service debug '{0}'".format(
                    stack_instance.services[service_name]))
                invoc.infrastructure_target = stack_instance.services[service_name].infrastructure_target
                invoc.stack_instance = stack_instance.name
                invoc.tool = fr_doc['invocation']['tool']
                invoc.service = service_name
                logger.debug(
                    "[GrpcAgentBroker] create_job_for_agent. Added fr '{0}' and invoc '{1}'"
                        .format(fr_doc, invoc.SerializeToString()))
                job.append(automation_message)
        return job
