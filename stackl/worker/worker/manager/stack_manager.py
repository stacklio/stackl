import logging

import stackl.stackl_globals as stackl_globals
from stackl.enums.cast_type import CastType
from stackl.enums.stackl_codes import StatusCode
from stackl.message_channel.message_channel_factory import MessageChannelFactory
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.result_task import ResultTask

from worker.agent_broker.agent_task_broker import AgentTaskBroker
from worker.handler.stack_handler import StackHandler
from worker.opa_broker.opa_broker_factory import OPABrokerFactory
from .manager import Manager

logger = logging.getLogger("STACKL_LOGGER")


class StackManager(Manager):
    def __init__(self):
        super(StackManager, self).__init__()

        self.agent_task_broker = AgentTaskBroker(stackl_globals.redis_cache)

        task_broker_factory = TaskBrokerFactory()
        self.task_broker = task_broker_factory.get_task_broker()

        opa_broker_factory = OPABrokerFactory()
        self.opa_broker = opa_broker_factory.get_opa_broker()

        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

        self.document_manager = None  # To be given after initalisation by manager_factory
        self.snapshot_manager = None  # To be given after initalisation by manager_factory

    def handle_task(self, task):
        logger.debug(f"[StackManager] handling stack_task '{task}'")
        stack_instance = None

        if task["subtype"] == "GET_STACK":
            (stack_instance_name) = task["args"]
            return_result = self.document_manager.get_document(
                type="stack_instance", name=stack_instance_name)
        elif task["subtype"] == "GET_ALL_STACKS":
            (stack_instance_name) = task["args"]
            return_result = self.document_manager.collect_documents(
                type_name="stack_instance", name=stack_instance_name)
        elif task["subtype"] == "CREATE_STACK":
            (stack_instance, return_result) = self._process_stack_request(
                task["json_data"], "create")
            if stack_instance is not None:
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "create", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
        elif task["subtype"] == "UPDATE_STACK":
            (stack_instance, return_result) = self._process_stack_request(
                task["json_data"], "update")
            # Lets not create the job object when we don't want an invocation
            if not return_result == StatusCode.BAD_REQUEST:
                if not stack_task["json_data"]["disable_invocation"]:
                    job = self.agent_broker.create_job_for_agent(
                        stack_instance, "update", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
        elif task[
                "subtype"] == "DELETE_STACK":  # TODO: Do we want to keep deleted stacks as documents?
            (stack_instance, return_result) = self._process_stack_request(
                task["json_data"], "delete")
            if not return_result == StatusCode.BAD_REQUEST:
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "delete", self.document_manager)
                stack_instance.deleted = True
                self.document_manager.write_stack_instance(stack_instance)
        else:
            return_result = StatusCode.BAD_REQUEST

        logger.debug(f"[StackManager] Handled StackTask")
        result_task = ResultTask({
            'channel': task.get('return_channel'),
            'cast_type': CastType.BROADCAST.value,
            'result_msg':
            f"StackTask with type '{task['subtype']}' was handled",
            'return_result': return_result,
            'result_code': StatusCode.OK,
            'source_task': task
        })
        self.message_channel.publish(result_task)

    # Rudimentary rollback system. It should also take into account the reason for the failure.
    # For instance, rollback create should behave differently if the failure was because the item already existed then when the problem occured during actual creation
    def rollback_task(self, task):
        logger.debug(f"[StackManager] rolling back stack_task '{task}'")
        if task["subtype"] == "GET_STACK":
            logger.debug(
                f"[StackManager] rollback_task GET_STACK. Safe Task. Nothing to do."
            )
        elif task["subtype"] == "GET_ALL_STACKS":
            logger.debug(
                f"[StackManager] rollback_task GET_ALL_STACKS. Safe Task. Nothing to do."
            )
        elif task["subtype"] == "CREATE_STACK":
            (stack_instance, return_result) = self._process_stack_request(
                task["json_data"], "delete"
            )  # TODO: Do we want to keep deleted stacks as documents?
            if not return_result == StatusCode.BAD_REQUEST:
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "delete", self.document_manager)
                stack_instance.deleted = True
                self.document_manager.write_stack_instance(stack_instance)
            logger.debug(
                f"[StackManager] rollback_task CREATE_STACK. Undo stack if it did not yet exist and was created. Result '{return_result}'"
            )
        elif task["subtype"] == "UPDATE_STACK":
            # First, we get and restore the previous stack_instance document
            previous_stack = self.snapshot_manager.get_snapshot(
                "stack_instance",
                task["json_data"]["stack_instance_name"])["snapshot"]
            self.snapshot_manager.restore_snapshot(
                "stack_instance", task["json_data"]["stack_instance_name"])
            # Second, we deploy this stack_instance
            (stack_instance, return_result) = self._process_stack_request(
                previous_stack, "update")
            # Lets not create the job object when we don't want an invocation
            if not return_result == StatusCode.BAD_REQUEST:
                if not previous_stack["disable_invocation"]:
                    self.agent_task_broker.create_job_for_agent(
                        stack_instance, "update", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
            logger.debug(
                f"[StackManager] rollback_task UPDATE_STACK. Restored latest snapshot of stack_instance doc and deployed it. Result '{return_result}'"
            )
        elif task["subtype"] == "DELETE_STACK":
            # First, we restore the previous stack_instance document
            previous_stack = self.snapshot_manager.restore_snapshot(
                "stack_instance", task["json_data"]["name"])
            # Second, we deploy this stack_instance
            (stack_instance, return_result) = self._process_stack_request(
                previous_stack, "update")
            # Lets not create the job object when we don't want an invocation
            if not return_result == StatusCode.BAD_REQUEST:
                if not previous_stack["disable_invocation"]:
                    self.agent_task_broker.create_job_for_agent(
                        stack_instance, "update", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
            logger.debug(
                f"[StackManager] rollback_task UPDATE_STACK. Restored latest snapshot of stack_instance doc and deployed it. Result '{return_result}'"
            )
        elif task["subtype"] == "DELETE_STACK":
            # First, we restore the previous stack_instance document
            previous_stack = self.snapshot_manager.restore_snapshot(
                "stack_instance", task["json_data"]["name"])
            # Second, we deploy this stack_instance
            (stack_instance, return_result) = self._process_stack_request(
                previous_stack, "update")
            # Lets not create the job object when we don't want an invocation
            if not return_result == StatusCode.BAD_REQUEST:
                if not previous_stack["disable_invocation"]:
                    self.agent_task_broker.create_job_for_agent(
                        stack_instance, "update", self.document_manager)
                self.document_manager.write_stack_instance(stack_instance)
            logger.debug(
                f"[StackManager] rollback_task DELETE_STACK. Restored stack_instance doc to latest snapshot if it was present and deployed it. Result '{return_result}'"
            )

    def _process_stack_request(self, instance_data, stack_action):
        # create new object with the action and document in it
        logger.debug(
            f"[StackManager] _process_stack_request. Converting instance data '{instance_data}' to job wrapper object"
        )
        if not self._validate_stack_request(instance_data, stack_action):
            logger.debug(
                f"[StackManager ] _process_stack_request. Validation failed. Returning StatusCode.BAD_REQUEST"
            )
            return {}, StatusCode.BAD_REQUEST

        job = {}
        job['action'] = stack_action
        job['document'] = instance_data
        job['type'] = 'stack_instance'
        handler = StackHandler(self.document_manager, self.opa_broker)
        merged_sat_sit_obj, err_message = handler.handle(job)
        logger.debug(
            f"[StackManager ]_process_stack_request. Handle complete. merged_sat_sit_obj '{merged_sat_sit_obj}'"
        )
        return merged_sat_sit_obj, err_message

    def _validate_stack_request(self, instance_data, stack_action):
        # check existence of stack_instance
        if "name" in instance_data:
            stack_name = instance_data["name"]
        else:
            stack_name = instance_data["stack_instance_name"]

        stack_instance_exists = self.document_manager.get_document(
            type="stack_instance", name=stack_name)
        logger.info(
            f"[StackManager] _validate_stack_request. stack_instance_exists: {not stack_instance_exists is {}}"
        )
        if stack_action == "create":
            if stack_instance_exists:
                return False
            # check if SIT exists
            infr_template_exists = self.document_manager.get_document(
                type="stack_infrastructure_template",
                name=instance_data["stack_infrastructure_template"])
            logger.info(
                f"[StackManager] _validate_stack_request. infr_template_exists (should be the case): {not infr_template_exists is {}}"
            )
            if not infr_template_exists:
                return False

            # check if SAT exists
            stack_application_template = self.document_manager.get_document(
                type='stack_application_template',
                name=instance_data["stack_application_template"])
            logger.info(
                f"[StackManager] _validate_stack_request. application_template_name exists (should be the case): {not stack_application_template is {}}"
            )
            if not stack_application_template:
                return False
            # Everything OK for create:
            return True
        elif stack_action == "update":
            return stack_instance_exists  # For UPDATE, OK if it exists
        elif stack_action == "delete":
            return stack_instance_exists
        return False
