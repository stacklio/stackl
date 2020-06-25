import json
import logging
import threading

from redis import StrictRedis
from stackl.models.items.stack_instance_status_model import StackInstanceStatus, Status
from stackl.task_broker.task_broker import TaskBroker
from stackl.tasks.document_task import DocumentTask
from stackl.tasks.result_task import ResultTask

from stackl.models.items.stack_instance_model import StackInstance

from stackl.enums.stackl_codes import StatusCode
from stackl_protos.agent_pb2 import AgentMetadata, ConnectionResult, Invocation, AutomationResult
from stackl_protos.agent_pb2_grpc import StacklAgentServicer

logger = logging.getLogger("STACKL_LOGGER")


class AutomationJobDispenser(StacklAgentServicer):
    def __init__(self, redis: StrictRedis, task_broker: TaskBroker):
        self.redis = redis
        self.task_broker = task_broker
        self.agent = None

    def RegisterAgent(self, agent_metadata: AgentMetadata, context):
        self.redis.set(f'agents/{agent_metadata.name}',
                       agent_metadata.selector)
        self.agent = agent_metadata.name
        connection_result = ConnectionResult()
        connection_result.success = True
        return connection_result

    def unregister_agent(self):
        print(f"Unregister agent")
        self.redis.delete(self.agent)
        threading.Event().set()

    def GetJob(self, agent_metadata: AgentMetadata, context):
        print(f"Request for job received")
        agent_p = self.redis.pubsub()
        agent_p.subscribe(agent_metadata.name)
        context.add_callback(self.unregister_agent)
        for message in agent_p.listen():
            print(f"Received message: {message}")
            invocation = Invocation()
            if message["type"] == "subscribe":
                continue
            message_json = json.loads(message["data"])
            try:
                invoc_message = message_json["invocation"]
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
            invocation.requester = message_json["return_channel"]
            invocation.source_task_id = invoc_message["source_task_id"]
            print(f"invocation {invocation}")
            yield invocation
        # TODO Lets check if listen fails if the connection drops, then this place would be perfect to deregister the agent
        print(f"Connection dropped, deregister agent #{agent_metadata.name}")

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

        self.task_broker.give_task(task)
        result = self.task_broker.get_task_result(task.id)

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

        self.task_broker.give_task(task)
        task = ResultTask.parse_obj({
            'channel': automation_result.requester,
            'result_msg':
            f"Finished provisioning {automation_result.functional_requirement} of {automation_result.service} on infrastructure target: {automation_result.infrastructure_target}",
            'return_result': "",
            'result_code': StatusCode.OK,
            'cast_type': "broadcast",
            'source_task_id': automation_result.source_task_id,
            'status': "progress"
        })

        self.task_broker.give_task(task)

        connection_result = ConnectionResult(success=True)
        return connection_result
