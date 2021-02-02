"""
Module for managing stack instances
"""
from typing import Dict, Any

from loguru import logger
from pydantic.main import BaseModel

from core.handler.stack_handler import StackHandler
from core.opa_broker.opa_broker_factory import OPABrokerFactory
from .document_manager import DocumentManager
from .manager import Manager


class OutputsUpdate(BaseModel):
    """OutputsUpdate Model"""
    stack_instance: str
    service: str
    infrastructure_target: str
    outputs: Dict[str, Any]


class StackManager(Manager):
    """Manager for Stack instances"""

    def __init__(self):
        super().__init__()

        opa_broker_factory = OPABrokerFactory()
        self.opa_broker = opa_broker_factory.get_opa_broker()

        self.document_manager = DocumentManager()

    def add_outputs(self, outputs_update: OutputsUpdate):
        """Method for adding outputs to a stack instance"""
        handler = StackHandler(self.document_manager, self.opa_broker)
        stack_instance = handler.add_outputs(outputs_update)
        return stack_instance

    def check_delete_services(self, instance_data):
        handler = StackHandler(self.document_manager, self.opa_broker)
        return handler.check_difference(instance_data)

    def process_stack_request(self, instance_data, stack_action):
        """prepares a create, update or delete of a stack instance"""
        # create new object with the action and document in it
        logger.debug(
            f"Converting instance data '{instance_data}' to job wrapper object"
        )
        valid, validation_error = self._validate_stack_request(
            instance_data, stack_action)
        if not valid:
            logger.debug(
                "Validation failed. Returning StatusCode.BAD_REQUEST"
            )
            return None, validation_error

        job = {}
        job['action'] = stack_action
        job['document'] = instance_data
        job['type'] = 'stack_instance'
        handler = StackHandler(self.document_manager, self.opa_broker)
        stack_instance, err_message = handler.handle(job)
        logger.debug(
            f"Handle complete. stack_instance '{stack_instance}'"
        )
        return stack_instance, err_message

    def _validate_stack_request(self, instance_data,
                                stack_action) -> (bool, str):
        """Validates a request for a stack instance"""
        # check existence of stack_instance
        if "name" in instance_data:
            stack_name = instance_data.name
        else:
            stack_name = instance_data.stack_instance_name

        stack_instance_exists = self.document_manager.get_document(
            type="stack_instance", name=stack_name)

        if stack_action == "create":
            if stack_instance_exists:
                return False, "Stack instance already exists"
            # check if SIT exists
            infr_template_exists = self.document_manager.get_document(
                type="stack_infrastructure_template",
                name=instance_data.stack_infrastructure_template)

            if not infr_template_exists:
                return False, "Stack infrastructure template: " \
                              f"{instance_data.stack_infrastructure_template} does not exist"

            # check if SAT exists
            stack_application_template = self.document_manager.get_document(
                type='stack_application_template',
                name=instance_data.stack_application_template)
            logger.info(
                "application_template_name exists (should be the case):"
                f" {bool(stack_application_template)}"
            )
            if not stack_application_template:
                return False, f"Stack application template: " \
                              f"{instance_data.stack_application_template} does not exist"
            # Everything OK for create:
            result = True, ""
        elif stack_action == "update":
            result = True, ""  # For UPDATE, OK if it exists
        elif stack_action == "delete":
            result = stack_instance_exists, ""
        return result
