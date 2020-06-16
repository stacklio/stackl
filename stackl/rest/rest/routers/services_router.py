import logging
from typing import List

from fastapi import APIRouter
from stackl.models.items.service_model import Service
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.document_task import DocumentTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[Service])
def get_services():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'service'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': "service",
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.get('/{name}', response_model=Service)
def get_service_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'service' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': ('service', name),
        'subtype': "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.post('', response_model=Service)
def post_service(document: Service):
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


@router.put('', response_model=Service)
def put_service(document: Service):
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
def delete_service(name: str):
    task = DocumentTask({
        'channel': 'worker',
        'args': ("service", name),
        'subtype': "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result
