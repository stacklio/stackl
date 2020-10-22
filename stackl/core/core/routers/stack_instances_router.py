"""
Endpoint used for creating, updating, reading and deleting stack instances
"""

from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from core.agent_broker.agent_task_broker import create_job_for_agent
from core.manager.document_manager import DocumentManager
from core.manager.stack_manager import StackManager
from core.manager.stackl_manager import get_document_manager, get_stack_manager, get_redis
from core.models.items.stack_instance_model import StackInstance

router = APIRouter()


class StackInstanceInvocation(BaseModel):
    """
    Possible options for creating a Stack Instance
    """
    params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    tags: Dict[str, str] = {}
    stack_infrastructure_template: str = "stackl"
    stack_application_template: str = "web"
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    replicas: Dict[str, int] = {}


class StackInstanceUpdate(BaseModel):
    """
    Options for updating a Stack Instance
    """
    params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    tags: Dict[str, str] = {}
    replicas: Dict[str, int] = {}
    disable_invocation: bool = False


class StackCreateResult(BaseModel):
    """StackCreateResult Model"""
    result: str


@router.get('/{name}', response_model=StackInstance)
def get_stack_instance(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a stack instance with a specific name"""
    logger.info(
        f"[StackInstancesName GET] Getting document for stack instance '{name}'"
    )
    stack_instance = document_manager.get_stack_instance(name)
    if not stack_instance:
        raise HTTPException(status_code=404, detail="Stack instance not found")
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
    """
    Updates a stack instance by using a StackInstanceUpdate object
    """
    logger.info("[StackInstances PUT] Received PUT request")

    (stack_instance, return_result) = stack_manager.process_stack_request(
        stack_instance_update, "update")
    if stack_instance is None:
        return HTTPException(422, return_result)

    document_manager.write_stack_instance(stack_instance)

    # Perform invocations
    if not stack_instance_update.disable_invocation:
        background_tasks.add_task(create_job_for_agent, stack_instance,
                                  "update", document_manager, redis)

    return return_result


@router.delete('/{name}')
def delete_stack_instance(
        name: str,
        background_tasks: BackgroundTasks,
        force: bool = False,
        document_manager: DocumentManager = Depends(get_document_manager),
        redis=Depends(get_redis)):
    """Delete a stack instance with a specific name"""
    stack_instance = document_manager.get_stack_instance(name)
    background_tasks.add_task(create_job_for_agent, stack_instance, "delete",
                              document_manager, redis, force_delete=force)

    return {"result": f"Deleting stack instance {name}"}
