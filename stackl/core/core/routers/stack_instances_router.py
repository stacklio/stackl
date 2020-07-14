import os
from typing import Dict, Any, List

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel  # pylint: disable=E0611 #pylint error
from stackl.models.items.stack_instance_model import StackInstance
from starlette.background import BackgroundTasks

from core.agent_broker.agent_task_broker import create_job_for_agent
from core.manager.document_manager import DocumentManager
from core.manager.stack_manager import StackManager
from core.manager.stackl_manager import get_document_manager, get_stack_manager

router = APIRouter()


class StackInstanceInvocation(BaseModel):
    params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    tags: Dict[str, str] = {}
    stack_infrastructure_template: str = "stackl"
    stack_application_template: str = "web"
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    replicas: Dict[str, int] = {}

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
    service_params: Dict[str, Dict[str, Any]] = {}
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


class StackCreateResult(BaseModel):
    result: str


async def get_redis():
    return await create_pool(
        RedisSettings(host=os.environ["REDIS_HOST"],
                      port=os.environ.get("REDIS_PORT", 6379)))


@router.get('/{name}', response_model=StackInstance)
def get_stack_instance(
    name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a stack instance with a specific name"""
    logger.info(
        f"[StackInstancesName GET] Getting document for stack instance '{name}'"
    )
    stack_instance = document_manager.get_stack_instance(name)
    return stack_instance


@router.get('', response_model=List[StackInstance])
def get_stack_instances(
    name: str = "",
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all stack instances that contain optional name"""
    logger.info(
        f"[StackInstancesAll GET] Returning all stack instances that contain optional name '{name}'"
    )
    stack_instances = document_manager.get_stack_instances()
    return stack_instances


@router.post('')
async def post_stack_instance(
    background_tasks: BackgroundTasks,
    stack_instance_invocation: StackInstanceInvocation,
    document_manager: DocumentManager = Depends(get_document_manager),
    stack_manager: StackManager = Depends(get_stack_manager),
    redis=Depends(get_redis)):
    """Creates a stack instance with a specific name"""
    logger.info("[StackInstances POST] Received POST request")
    (stack_instance, return_result) = stack_manager.process_stack_request(
        stack_instance_invocation, "create")
    if stack_instance is None:
        return HTTPException(422, return_result)

    document_manager.write_stack_instance(stack_instance)
    # Perform invocations
    background_tasks.add_task(create_job_for_agent, stack_instance, "create",
                              document_manager, redis)
    return return_result


@router.put('')
async def put_stack_instance(
    background_tasks: BackgroundTasks,
    stack_instance_update: StackInstanceUpdate,
    document_manager: DocumentManager = Depends(get_document_manager),
    stack_manager: StackManager = Depends(get_stack_manager),
    redis=Depends(get_redis)):
    """Update a stack instance with the given name from a stack application template and stack infrastructure template, creating a new one if it does not yet exist"""
    logger.info("[StackInstances PUT] Received PUT request")

    (stack_instance, return_result) = stack_manager.process_stack_request(
        stack_instance_update, "update")
    if stack_instance is None:
        return HTTPException(422, return_result)

    document_manager.write_stack_instance(stack_instance)

    # Perform invocations
    background_tasks.add_task(create_job_for_agent, stack_instance, "update",
                              document_manager, redis)

    return {"result": "stack instance updating"}


@router.delete('/{name}')
def delete_stack_instance(name: str):
    """Delete a stack instance with a specific name"""
    pass
    # logger.info(f"[StackInstances DELETE] Received DELETE request for {name}")
    # json_data = {}
    # json_data['name'] = name
    # task = StackTask.parse_obj({
    #     'channel': 'worker',
    #     'json_data': json_data,
    #     'subtype': "DELETE_STACK",
    # })
    # logger.info(
    #     f"[StackInstances DELETE] Giving StackTask '{dict(task)}' to task_broker"
    # )
    #
    # result = producer.give_task_and_get_result(task)
    #
    # if not StatusCode.is_successful(result):
    #     raise HTTPException(status_code=StatusCode.BAD_REQUEST,
    #                         detail="NOT OK!")
    # return result
