import json
import logging
import threading

from redis import StrictRedis

import model
from manager.document_manager import DocumentManager
from model.items.functional_requirement_status_model import FunctionalRequirementStatus
from model.items.stack_instance_status_model import StackInstanceStatus
from protos.agent_pb2 import AgentMetadata, Invocation, ConnectionResult, AutomationResult, Status
from protos.agent_pb2_grpc import StacklAgentServicer

logger = logging.getLogger("STACKL_LOGGER")


class AutomationJobDispenser(StacklAgentServicer):
    def __init__(self, redis: StrictRedis, document_manager: DocumentManager):
        self.redis = redis
        self.document_manager = document_manager
        self.agent = None

    def RegisterAgent(self, agent_metadata: AgentMetadata, context):
        self.redis.set(f'agents/{agent_metadata.name}',
                       agent_metadata.selector)
        self.agent = agent_metadata.name
        connection_result = ConnectionResult()
        connection_result.success = True
        return connection_result

    def unregister_agent(self):
        logger.debug(f"Unregister agent")
        self.redis.delete(self.agent)
        threading.Event().set()

    def GetJob(self, agent_metadata: AgentMetadata, context):
        logger.debug(f"Request for job received")
        agent_p = self.redis.pubsub()
        agent_p.subscribe(agent_metadata.name)
        context.add_callback(self.unregister_agent)
        for message in agent_p.listen():
            logger.debug(f"Received message: {message}")
            invocation = Invocation()
            try:
                invoc_message = json.loads(message["data"])
            except TypeError:
                continue
            invocation.image = invoc_message["image"]
            invocation.infrastructure_target = invoc_message[
                "infrastructure_target"]
            invocation.stack_instance = invoc_message["stack_instance"]
            invocation.service = invoc_message["service"]
            invocation.functional_requirement = invoc_message[
                "functional_requirement"]
            invocation.tool = invoc_message["tool"]
            invocation.action = invoc_message["action"]
            logger.debug(f"invocation {invocation}")
            yield invocation
        # TODO Lets check if listen fails if the connection drops, then this place would be perfect to deregister the agent
        logger.debug(
            f"Connection dropped, deregister agent #{agent_metadata.name}")

    def ReportResult(self, automation_result: AutomationResult, context):
        logger.info(
            f"[AutomationJobDispenser] processing result {automation_result}")
        stack_instance = self.document_manager.get_stack_instance(
            automation_result.stack_instance)

        stack_instance_status = StackInstanceStatus()
        stack_instance_status.service = automation_result.service
        stack_instance_status.functional_requirement = automation_result.functional_requirement
        stack_instance_status.infrastructure_target = automation_result.infrastructure_target

        if hasattr(automation_result, 'error_message'):
            error_message = automation_result.error_message
        else:
            error_message = ""

        if hasattr(automation_result, 'status'):
            status = model.items.stack_instance_status_model.Status(
                automation_result.status)
        else:
            status = model.items.stack_instance_status_model.Status.READY

        stack_instance_status.status = status
        stack_instance_status.error_message = error_message

        changed = False
        for i, status in enumerate(stack_instance.status):
            if status.functional_requirement == automation_result.functional_requirement and status.infrastructure_target == automation_result.infrastructure_target and status.service == automation_result.service:
                stack_instance.status[i] = stack_instance_status
                changed = True
                break

        if not changed:
            stack_instance.status.append(stack_instance_status)

        logger.info(f"[AutomationJobDispenser] done processing")
        self.document_manager.write_stack_instance(stack_instance)
        connection_result = ConnectionResult(success=True)
        return connection_result