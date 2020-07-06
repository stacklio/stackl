import logging

from stackl.models.items.stack_instance_model import StackInstance
from stackl.models.items.stack_instance_status_model import StackInstanceStatus, Status
from stackl.tasks.agent_task import AgentTask
from stackl.tasks.document_task import DocumentTask

from job_broker.message_channel.message_channel_factory import get_message_channel
from stackl_protos.agent_pb2 import AgentMetadata, ConnectionResult, Invocation, AutomationResult
from stackl_protos.agent_pb2_grpc import StacklAgentServicer

logger = logging.getLogger("STACKL_LOGGER")


class AutomationJobDispenser(StacklAgentServicer):
    def __init__(self):
        self.message_channel = get_message_channel()
        self.agent = None

    def RegisterAgent(self, agent_metadata: AgentMetadata, context):
        self.message_channel.register_agent(agent_metadata.name,
                                            agent_metadata.selector)
        self.agent = agent_metadata.name
        connection_result = ConnectionResult()
        connection_result.success = True
        return connection_result

    def _unregister_agent(self):
        print(f"Connection dropped, deregister agent #{self.agent}")
        self.message_channel.unregister_agent(self.agent)

    def process_agent_task(self, task: AgentTask):
        print(f"Received agent task: {task}")
        invocation = Invocation()
        invocation.image = task.invocation["image"]
        invocation.infrastructure_target = task.invocation[
            "infrastructure_target"]
        invocation.stack_instance = task.invocation["stack_instance"]
        invocation.service = task.invocation["service"]
        invocation.functional_requirement = task.invocation[
            "functional_requirement"]
        invocation.tool = task.invocation["tool"]
        invocation.action = task.invocation["action"]
        invocation.source_task_id = task.invocation["source_task_id"]
        print(f"invocation {invocation}")
        return invocation

    def GetJob(self, agent_metadata: AgentMetadata, context):
        print(f"Request for job received")
        context.add_callback(self._unregister_agent)
        invocations = self.message_channel.listen_for_jobs(
            self.process_agent_task)
        for invoc in invocations:
            yield invoc

    def ReportResult(self, automation_result: AutomationResult, context):
        print(
            f"[AutomationJobDispenser] processing result {automation_result}")

        task = DocumentTask.parse_obj({
            'channel':
            'worker',
            'subtype':
            "GET_DOCUMENT",
            'args': ('stack_instance', automation_result.stack_instance)
        })

        result = self.message_channel.give_task_and_get_result(task)

        stack_instance_dict = result.return_result
        stack_instance = StackInstance.parse_obj(stack_instance_dict)

        stack_instance_status = StackInstanceStatus()
        stack_instance_status.service = automation_result.service
        stack_instance_status.functional_requirement = automation_result.functional_requirement
        stack_instance_status.infrastructure_target = automation_result.infrastructure_target

        if hasattr(automation_result, 'error_message'):
            error_message = automation_result.error_message
        else:
            error_message = ""

        if hasattr(automation_result, 'status'):
            status = Status(automation_result.status)
        else:
            status = Status.READY

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

        print(f"[AutomationJobDispenser] done processing")
        task = DocumentTask.parse_obj({
            'channel': 'worker',
            'document': stack_instance.dict(),
            'subtype': "PUT_DOCUMENT"
        })

        self.message_channel.give_task_and_get_result(task)

        connection_result = ConnectionResult(success=True)
        return connection_result
