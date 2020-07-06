import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.stack_application_template_model import StackApplicationTemplate
from stackl.tasks.document_task import DocumentTask

from rest.producer.producer_factory import get_producer

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

producer = get_producer()


@router.get('', response_model=List[StackApplicationTemplate])
def get_stack_application_templates():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'stack_application_templates'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': "stack_application_template",
        'subtype': "COLLECT_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.get('/{name}', response_model=StackApplicationTemplate)
def get_stack_application_template_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'stack_application_template' and document '{name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ('stack_application_template', name),
        'subtype': "GET_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.post('', response_model=StackApplicationTemplate)
def post_stack_application_template(document: StackApplicationTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.put('', response_model=StackApplicationTemplate)
def put_stack_application_template(document: StackApplicationTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.delete('/{name}', status_code=202)
def delete_stack_application_template(name: str):
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ("stack_application_template", name),
        'subtype': "DELETE_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result
