import logging
from typing import Dict, Any
from collections.abc import Collection
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel  # pylint: disable=E0611 #pylint error

from enums.stackl_codes import StatusCode
from model.configs.document_model import CollectionDocument
from task.stack_task import StackTask
from task_broker.task_broker_factory import TaskBrokerFactory

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()
task_broker = TaskBrokerFactory().get_task_broker()


class StackInstanceInvocation(BaseModel):
    params: Dict[str, Any] = {}
    tags: Dict[str, str] = {}
    stack_infrastructure_template: str = "stackl"
    stack_application_template: str = "web"
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}

    class Config:
        schema_extra = {
            "example": {
                "params": {},
                "secrets": {},
                "stack_infrastructure_template": "stackl",
                "stack_application_template": "web",
                "name": "default_test_instance"
            }
        }


class StackInstanceUpdate(BaseModel):
    params: Dict[str, Any] = {}
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    disable_invocation: bool = False

    class Config:
        schema_extra = {
            "example": {
                "params": {},
                "secrets": {},
                "stack_instance_name": "default_test_instance"
            }
        }


@router.get('/{name}')
async def get_stack_instance(name: str):
    """Returns a stack instance with a specific name"""
    logger.info(
        f"[StackInstancesName GET] Getting document for stack instance '{name}'"
    )
    task = StackTask({
        'channel': 'worker',
        'subtype': "GET_STACK",
        'args': (name)
    })
    logger.info(
        f"[StackInstances POST] Giving StackTask '{task.__dict__}' to task_broker"
    )
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if not isinstance(result, Collection):
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='Stack instance ' + str(name) +
                            ' not found')
    return result


@router.get('/all/')
async def get_stack_instances(name: str = ""):
    """Returns all stack instances that contain optional name"""
    logger.info(
        f"[StackInstancesAll GET] Returning all stack instances that contain optional name '{name}'"
    )
    task = StackTask({
        'channel': 'worker',
        'subtype': "GET_ALL_STACKS",
        'args': (name)
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    document: CollectionDocument = {
        "name": "CollectionDocumentByType_" + "stack_instance",
        "description":
        "Document that contains all the documents by type " + "stack_instance",
        "type": "stack_instance",
        "documents": result
    }
    if not isinstance(result, Collection):
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail='Stack instances ' + str(name) +
                            ' not found')
    return document


@router.post('')
async def post_stack_instance(stack_instance_invocation: StackInstanceInvocation):
    """Creates a stack instance with a specific name"""
    logger.info("[StackInstances POST] Received POST request")

    task = StackTask({
        'channel': 'worker',
        'json_data': stack_instance_invocation.dict(),
        'subtype': "CREATE_STACK",
    })
    logger.info(
        f"[StackInstances POST] Giving StackTask '{task.__dict__}' to task_broker"
    )

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if not StatusCode.is_successful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return {
        'return_code': result,
        'message': 'Stack instance creating'
    }, result


@router.put('')
async def put_stack_instance(stack_instance_update: StackInstanceUpdate):
    """Update a stack instance with the given name from a stack application template and stack infrastructure template, creating a new one if it does not yet exist"""
    logger.info("[StackInstances PUT] Received PUT request")

    task = StackTask({
        'channel': 'worker',
        'json_data': stack_instance_update.dict(),
        'subtype': "UPDATE_STACK",
    })
    logger.info(
        f"[StackInstances PUT] Giving StackTask '{task}' to task_broker")
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if not StatusCode.is_successful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")

    return {
        'return_code': StatusCode.ACCEPTED,
        'message': 'Stack instance updating'
    }, StatusCode.ACCEPTED


@router.delete('/{name}')
async def delete_stack_instance(name: str):
    """Delete a stack instance with a specific name"""
    logger.info(f"[StackInstances DELETE] Received DELETE request for {name}")
    json_data = {}
    json_data['name'] = name
    task = StackTask({
        'channel': 'worker',
        'json_data': json_data,
        'subtype': "DELETE_STACK",
    })
    logger.info(
        f"[StackInstances DELETE] Giving StackTask '{task.__dict__}' to task_broker"
    )

    result = await task_broker.give_task(task)

    if not StatusCode.is_successful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result
