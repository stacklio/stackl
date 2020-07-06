import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.policy_template_model import PolicyTemplate
from stackl.tasks.document_task import DocumentTask

from rest.producer.producer_factory import get_producer

logger = logging.getLogger(__name__)
router = APIRouter()

producer = get_producer()


@router.get('', response_model=List[PolicyTemplate])
def get_policy_templates():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'policy_template'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': "policy_template",
        'subtype': "COLLECT_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.get('/{policy_name}', response_model=PolicyTemplate)
def get_policy_template_by_name(policy_name: str):
    """Returns a policy template"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'policy_template' and document '{policy_name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ('policy_template', policy_name),
        'subtype': "GET_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.put('')
def put_policy_template(policy: PolicyTemplate):
    logger.info(
        f"[PutDocument] API PUT request with policy_template: {policy}")
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': policy.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    producer.give_task_and_get_result(task)
    return policy
