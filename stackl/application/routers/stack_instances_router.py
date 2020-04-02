import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel #pylint: disable=E0611 #pylint error

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.items.stack_instance_model import StackInstance
from model.items.stack_instance_service_model import ConnectionCredentials
from task.stack_task import StackTask
from task_broker.task_broker_factory import TaskBrokerFactory


logger = logging.getLogger("STACKL_LOGGER")

router = APIRouter()

manager_factory = ManagerFactory()
document_manager = manager_factory.get_document_manager()
user_manager = manager_factory.get_user_manager()
stack_manager = manager_factory.get_stack_manager()
task_broker_factory = TaskBrokerFactory()
task_broker = task_broker_factory.get_task_broker()

example_stack_instance_invocation = {
    "params" : {},
    "connection_credentials": {"username": "example_user", "password": "example_pwd"},
    "stack_infrastructure_template": "stackl",
    "stack_application_template": "web",
    "stack_instance_name": "default_test_instance"
}

class StackInstanceInvocation(BaseModel):
    params: Dict[str, Any] = {}
    connection_credentials: ConnectionCredentials = None
    stack_infrastructure_template: str = "stackl"
    stack_application_template: str = "web"
    stack_instance_name: str = "default_test_instance"


@router.get('/{stack_instance_name}', response_model=StackInstance)
def get_stack_instance(stack_instance_name: str):
    """Returns a stack instance with a specific name"""
    logger.info(
        f"[StackInstancesName GET] Getting document for stack instance {stack_instance_name} using manager")
    stack_instance = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
    if not stack_instance:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='Stack instance ' + str(stack_instance_name) + ' not found')
    return stack_instance


@router.get('', response_model=List[StackInstance])
def get_stack_instances():
    """Returns all stack instances"""
    logger.info("[StackInstancesAll GET] Returning all stack instances")
    doc = document_manager.get_document(type="stack_instance")
    if doc:
        return doc
    else:
        return {}


@router.post('')
def post_stack_instance(stack_instance_invocation: StackInstanceInvocation = Body(..., example=example_stack_instance_invocation)):
    """Creates a stack instance with a specific name"""
    logger.info("[StackInstances POST] Received POST request")
    # check if SIT exists
    infr_template_exists = document_manager.get_document(type="stack_infrastructure_template",
                                                         document_name=stack_instance_invocation.stack_infrastructure_template)
    logger.info(f"[StackInstances POST] infr_template_exists (should be the case): {infr_template_exists}")
    if not infr_template_exists:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='SIT with name ' + str(infr_template_exists) + ' does not exist')

    # check if SAT exists
    stack_application_template = document_manager.get_document(type='stack_application_template',
                                                               document_name=stack_instance_invocation.stack_application_template)
    logger.info(f"[StackInstances POST] application_template_name exists (should be the case): {stack_application_template}")
    if not stack_application_template:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='SAT with name ' + str(infr_template_exists) + ' does not exist')

    # check if stack_instance already exists. Should not be the case
    stack_instance_exists = document_manager.get_document(type="stack_instance",
                                                          document_name=stack_instance_invocation.stack_instance_name)
    logger.info(f"[StackInstances POST] stack_instance_exists (should not be case): {stack_instance_exists}")
    if stack_instance_exists:
        raise HTTPException(status_code=StatusCode.CONFLICT,
                            detail='SI with name ' + str(
                                stack_instance_invocation.stack_instance_name) + ' already exists')
    try:
        task = StackTask({
            'channel': 'worker',
            'json_data': stack_instance_invocation.dict(),
            'subtasks': ["CREATE"],
        })
        logger.info(f"[StackInstances POST] Giving StackTask '{task.__dict__}' to task_broker")
        task_broker.give_task(task)

        return {'return_code': StatusCode.CREATED, 'message': 'Stack instance creating'}, StatusCode.CREATED
    except Exception as e: #TODO TBD: When fixing robustness during Task Rework
        logger.error(f"[StackInstances POST] ERROR!!! rest api: {e}")
        return {'return_code': StatusCode.INTERNAL_ERROR,
                'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@router.put('')
def put_stack_instance(stack_instance_invocation: StackInstanceInvocation = Body(..., example=example_stack_instance_invocation)):
    """Update a stack instance with the given name from a stack application template and stack infrastructure template, creating a new one if it does not yet exist"""
    logger.info("[StackInstances POST] Received POST request")
    # check if SIT exists
    infr_template_exists = document_manager.get_document(type="stack_infrastructure_template",
                                                         document_name=stack_instance_invocation.stack_infrastructure_template)
    logger.info(f"[StackInstances POST] infr_template_exists (should be the case): {infr_template_exists}")
    if not infr_template_exists:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='SIT with name ' + str(infr_template_exists) + ' does not exist')

    # check if SAT exists
    stack_application_template = document_manager.get_document(type='stack_application_template',
                                                               document_name=stack_instance_invocation.stack_application_template)
    logger.info(f"[StackInstances POST] application_template_name exists (should be the case): {stack_application_template}")
    if not stack_application_template:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='SAT with name ' + str(infr_template_exists) + ' does not exist')

    try:
        task = StackTask({
            'channel': 'worker',
            'json_data': stack_instance_invocation.dict(),
            'subtasks': ["UPDATE"]
        })
        logger.info(f"[StackInstances PUT] Giving StackTask '{task}' to task_broker")
        task_broker.give_task(task)

        return {'return_code': StatusCode.CREATED, 'message': 'Stack instance updating'}, StatusCode.CREATED
    except Exception as e:  #TODO TBD: When fixing robustness during Task Rework
        logger.error(f"[StackInstances PUT] ERROR!!! rest api: {e}")
        return {'return_code': StatusCode.INTERNAL_ERROR,
                'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@router.delete('/{stack_instance_name}')
def delete_stack_instance(stack_instance_name: str):
    """Delete a stack instance with a specific name"""
    logger.info(f"[StackInstances DELETE] Received DELETE request for {stack_instance_name}")
    stack_instance_exists = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
    if not stack_instance_exists:
        return {'return_code': StatusCode.NOT_FOUND,
                'message': 'Stack instance ' + str(stack_instance_name) + ' not found'}, StatusCode.NOT_FOUND
    try:
        json_data = {}
        json_data['stack_instance_name'] = stack_instance_name
        task = StackTask({
            'channel': 'worker',
            'json_data': json_data,
            'subtasks': ["DELETE"],
        })
        logger.info(f"[StackInstances DELETE] Giving StackTask '{task.__dict__}' to task_broker")
        task_broker.give_task(task)
        return {'return_code': StatusCode.CREATED, 'message': 'Stack instance deleting'}, StatusCode.CREATED
    except Exception as e:  #TODO TBD: When fixing robustness during Task Rework
        return {'return_code': StatusCode.INTERNAL_ERROR,
                'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR
