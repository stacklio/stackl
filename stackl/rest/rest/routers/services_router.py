import logging
from typing import List

from fastapi import APIRouter
from stackl.models.items.service_model import Service
from stackl.models.items.stack_instance_model import StackInstance
from stackl.tasks.document_task import DocumentTask

from rest.producer.producer_factory import get_producer

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

producer = get_producer()


@router.get('', response_model=List[Service])
def get_services():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'service'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': "service",
        'subtype': "COLLECT_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.get('/{name}', response_model=Service)
def get_service_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'service' and document '{name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ('service', name),
        'subtype': "GET_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.post('', response_model=Service)
def post_service(document: Service):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.put('', response_model=Service)
def put_service(document: Service):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.delete('/{name}', status_code=202)
def delete_service(name: str):
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ("service", name),
        'subtype': "DELETE_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result
