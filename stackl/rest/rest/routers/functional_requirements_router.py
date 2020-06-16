import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.functional_requirement_model import FunctionalRequirement
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.document_task import DocumentTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[FunctionalRequirement])
def get_functional_requirements():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'policy_template'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': "functional_requirement",
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.get('/{name}', response_model=FunctionalRequirement)
def get_functional_requirement_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'policy_template' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': ('functional_requirement', name),
        'subtype': "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)
    return result.return_result


@router.post('', response_model=FunctionalRequirement)
def post_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    task_broker.give_task(task)
    task_broker.get_task_result(task.id)

    return document


@router.put('', response_model=FunctionalRequirement)
def put_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    task_broker.get_task_result(task.id)

    return document


@router.delete('/{name}', status_code=202)
def delete_functional_requirement(type_name: str, name: str):
    logger.info(
        f"[DeleteDocument] API Delete request for type '{type_name}' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result
