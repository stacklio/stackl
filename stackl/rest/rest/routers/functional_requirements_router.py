import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.functional_requirement_model import FunctionalRequirement
from stackl.tasks.document_task import DocumentTask

from rest.producer.producer_factory import get_producer

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

producer = get_producer()


@router.get('', response_model=List[FunctionalRequirement])
def get_functional_requirements():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'policy_template'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': "functional_requirement",
        'subtype': "COLLECT_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.get('/{name}', response_model=FunctionalRequirement)
def get_functional_requirement_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'policy_template' and document '{name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ('functional_requirement', name),
        'subtype': "GET_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)
    return result.return_result


@router.post('', response_model=FunctionalRequirement)
def post_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.put('', response_model=FunctionalRequirement)
def put_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.delete('/{name}', status_code=202)
def delete_functional_requirement(type_name: str, name: str):
    logger.info(
        f"[DeleteDocument] API Delete request for type '{type_name}' and document '{name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "DELETE_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result
