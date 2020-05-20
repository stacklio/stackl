import logging

import stackl_globals
from agent_broker.agent_task_broker import AgentTaskBroker
from enums.cast_type import CastType
from enums.stackl_codes import StatusCode
from handler.stack_handler import StackHandler
from manager import Manager
from opa_broker.opa_broker_factory import OPABrokerFactory
from task.result_task import ResultTask
from task_broker.task_broker_factory import TaskBrokerFactory

logger = logging.getLogger("STACKL_LOGGER")


##TODO this class and its terminology need to be updated significantly.
class StackManager(Manager):
    def __init__(self):
        super(StackManager, self).__init__()

        self.agent_task_broker = AgentTaskBroker(stackl_globals.redis_cache)

        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

        self.opa_broker_factory = OPABrokerFactory()
        self.opa_broker = self.opa_broker_factory.get_opa_broker()

        self.document_manager = None  #To be given after initalisation by manager_factory

    def handle_task(self, stack_task):
        logger.debug(f"[StackManager] handling stack_task '{stack_task}'")
        try:
            stack_instance = None
            if stack_task["subtype"] == "CREATE_STACK":
                (stack_instance, status_code) = self.process_stack_request(
                    stack_task["json_data"], "create")
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "create", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
            elif stack_task["subtype"] == "UPDATE_STACK":
                (stack_instance, status_code) = self.process_stack_request(
                    stack_task["json_data"], "update")
                # Lets not create the job object when we don't want an invocation
                if not stack_task["json_data"]["disable_invocation"]:
                    self.agent_task_broker.create_job_for_agent(
                        stack_instance, "update", self.document_manager)
                else:
                    job = []
                self.document_manager.write_stack_instance(stack_instance)
            elif stack_task["subtype"] == "DELETE_STACK":
                (stack_instance, status_code) = self.process_stack_request(
                    stack_task["json_data"], "delete")
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "delete", self.document_manager)
                stack_instance.deleted = True
                self.document_manager.write_stack_instance(stack_instance)
            else:
                status_code = StatusCode.BAD_REQUEST
            logger.debug(
                f"[StackManager] Succesfully handled StackTask with type '{stack_task['subtype']}'. Stack_instance: '{stack_instance}'."
            )
            self.task_broker.give_task(
                ResultTask({
                    'channel': stack_task.get('return_channel'),
                    'cast_type': CastType.BROADCAST.value,
                    'result_msg':
                    f"StackTask with type '{stack_task['subtype']}' was handled",
                    'result': str(stack_instance),
                    'cast_type': CastType.BROADCAST.value,
                    'source_task': stack_task
                })
            )  # this way the broker is notified of the result and whether he should remove the task from the task queue
        except Exception as e:
            logger.error(
                "[StackManager] Error with processing task. Error: '{0}'".
                format(e),
                exc_info=True)

    def process_stack_request(self, instance_data, stack_action):
        # create new object with the action and document in it
        logger.debug(
            "[StackManager] converting instance data to change wrapper object")
        job = {}
        job['action'] = stack_action
        job['document'] = instance_data
        job['type'] = 'stack_instance'
        handler = StackHandler(self.document_manager, self.opa_broker)
        merged_sat_sit_obj, status_code = handler.handle(job)
        logger.debug(
            "[StackManager] Handle complete. status_code '{0}'. merged_sat_sit_obj '{1}' "
            .format(status_code, merged_sat_sit_obj))
        return merged_sat_sit_obj, status_code
