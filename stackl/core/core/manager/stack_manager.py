import logging

from stackl.enums.cast_type import CastType
from stackl.enums.stackl_codes import StatusCode
from stackl.tasks.result_task import ResultTask

from core.handler.stack_handler import StackHandler
from core.opa_broker.opa_broker_factory import OPABrokerFactory
from stackl.models.items.stack_instance_model import StackInstance

from .document_manager import DocumentManager
from .manager import Manager

from loguru import logger


class StackManager(Manager):
    def __init__(self):
        super(StackManager, self).__init__()

        opa_broker_factory = OPABrokerFactory()
        self.opa_broker = opa_broker_factory.get_opa_broker()

        self.document_manager = DocumentManager()

    def handle_task(self, task):
        logger.debug(f"[StackManager] handling stack_task '{task}'")

        result_msg = None

        if task.subtype == "UPDATE_STACK":
            (stack_instance, return_result) = self._process_stack_request(
                task.json_data, "update")
            # Lets not create the job object when we don't want an invocation
            if stack_instance is not None and not task.json_data[
                    "disable_invocation"]:
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "update", self.document_manager,
                    task.return_channel, task.id)
                self.document_manager.write_stack_instance(stack_instance)
        elif task.subtype == "DELETE_STACK":  # TODO: Do we want to keep deleted stacks as documents?
            (stack_instance, return_result) = self._process_stack_request(
                task.json_data, "delete")
            if not return_result == StatusCode.BAD_REQUEST:
                self.agent_task_broker.create_job_for_agent(
                    stack_instance, "delete", self.document_manager)
                stack_instance.deleted = True
                self.document_manager.write_stack_instance(stack_instance)
        else:
            return_result = StatusCode.BAD_REQUEST

        logger.debug(f"[StackManager] Handled StackTask")
        result_task = ResultTask.parse_obj({
            'channel': task.return_channel,
            'cast_type': CastType.BROADCAST.value,
            'result_msg': result_msg,
            'return_result': return_result,
            'result_code': StatusCode.OK,
            'source_task': task,
            'status': "done",
            'source_task_id': task.id
        })
        return result_task

    def process_stack_request(self, instance_data, stack_action):
        # create new object with the action and document in it
        logger.debug(
            f"[StackManager] _process_stack_request. Converting instance data '{instance_data}' to job wrapper object"
        )
        if not self._validate_stack_request(instance_data, stack_action):
            logger.debug(
                f"[StackManager ] _process_stack_request. Validation failed. Returning StatusCode.BAD_REQUEST"
            )
            return None, "Validate stack request failed, stack instance probably already exists"

        job = {}
        job['action'] = stack_action
        job['document'] = instance_data
        job['type'] = 'stack_instance'
        handler = StackHandler(self.document_manager, self.opa_broker)
        stack_instance, err_message = handler.handle(job)
        logger.debug(
            f"[StackManager ]_process_stack_request. Handle complete. stack_instance '{stack_instance}'"
        )
        return stack_instance, err_message

    def rollback_task(self, task):
        pass

    def _validate_stack_request(self, instance_data, stack_action):
        # check existence of stack_instance
        if "name" in instance_data:
            stack_name = instance_data.name
        else:
            stack_name = instance_data.stack_instance_name

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
                name=instance_data.stack_infrastructure_template)
            logger.info(
                f"[StackManager] _validate_stack_request. infr_template_exists (should be the case): {not infr_template_exists is {}}"
            )
            if not infr_template_exists:
                return False

            # check if SAT exists
            stack_application_template = self.document_manager.get_document(
                type='stack_application_template',
                name=instance_data.stack_application_template)
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
