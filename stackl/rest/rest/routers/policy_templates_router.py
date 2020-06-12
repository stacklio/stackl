import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.policy_template_model import PolicyTemplate
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.document_task import DocumentTask

logger = logging.getLogger(__name__)
router = APIRouter()

task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[PolicyTemplate])
async def get_policy_templates():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'policy_template'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': "policy_template",
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    return result


@router.get('/{policy_name}', response_model=PolicyTemplate)
async def get_policy_template_by_name(policy_name: str):
    """Returns a policy template"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'policy_template' and document '{policy_name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': ('policy_template', policy_name),
        'subtype': "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    return result


@router.put('')
async def put_policy_template(policy: PolicyTemplate):
    logger.info(
        f"[PutDocument] API PUT request with policy_template: {policy}")
    task = DocumentTask({
        'channel': 'worker',
        'document': policy.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    logger.info(f"[PutDocument] API PUT request with result: '{result}'")
    return result
