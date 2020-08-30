from typing import Dict, Any

from loguru import logger
from pydantic.main import BaseModel

from core.handler.stack_handler import StackHandler
from core.opa_broker.opa_broker_factory import OPABrokerFactory
from .document_manager import DocumentManager
from .manager import Manager


class OutputsUpdate(BaseModel):
    stack_instance: str
    service: str
    infrastructure_target: str
    outputs: Dict[str, Any]

class StackManager(Manager):
    def __init__(self):
        super(StackManager, self).__init__()

        opa_broker_factory = OPABrokerFactory()
        self.opa_broker = opa_broker_factory.get_opa_broker()

        self.document_manager = DocumentManager()

    def add_outputs(self, outputs_update: OutputsUpdate):
        handler = StackHandler(self.document_manager, self.opa_broker)
        stack_instance = handler.add_outputs(outputs_update)
        return stack_instance

    def process_stack_request(self, instance_data, stack_action):
        # create new object with the action and document in it
        logger.debug(
            f"[StackManager] _process_stack_request. Converting instance data '{instance_data}' to job wrapper object"
        )
        valid, validation_error = self._validate_stack_request(
            instance_data, stack_action)
        if not valid:
            logger.debug(
                f"[StackManager ] _process_stack_request. Validation failed. Returning StatusCode.BAD_REQUEST"
            )
            return None, validation_error

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

    def _validate_stack_request(self, instance_data,
                                stack_action) -> (bool, str):
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
                return False, "Stack instance already exists"
            # check if SIT exists
            infr_template_exists = self.document_manager.get_document(
                type="stack_infrastructure_template",
                name=instance_data.stack_infrastructure_template)
            logger.info(
                f"[StackManager] _validate_stack_request. infr_template_exists (should be the case): {not infr_template_exists is {}}"
            )
            if not infr_template_exists:
                return False, f"Stack infrastructure template: {instance_data.stack_infrastructure_template} does not exist"

            # check if SAT exists
            stack_application_template = self.document_manager.get_document(
                type='stack_application_template',
                name=instance_data.stack_application_template)
            logger.info(
                f"[StackManager] _validate_stack_request. application_template_name exists (should be the case): {not stack_application_template is {}}"
            )
            if not stack_application_template:
                return False, f"Stack application template: {instance_data.stack_application_template} does not exist"
            # Everything OK for create:
            return True, ""
        elif stack_action == "update":
            return True, ""  # For UPDATE, OK if it exists
        elif stack_action == "delete":
            return stack_instance_exists
        return False, ""


