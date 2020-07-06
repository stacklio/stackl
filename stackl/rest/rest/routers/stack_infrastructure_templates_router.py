import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from stackl.tasks.document_task import DocumentTask

from rest.producer.producer_factory import get_producer

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

producer = get_producer()


@router.get('', response_model=List[StackInfrastructureTemplate])
def get_stack_infrastructure_templates():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'stack_infrastructrure_templates'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': "stack_infrastructure_template",
        'subtype': "COLLECT_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.get('/{name}', response_model=StackInfrastructureTemplate)
def get_stack_infrastructure_template_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'stack_infrastructure_template' and document '{name}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': ('stack_application_template', name),
        'subtype': "GET_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result


@router.post('', response_model=StackInfrastructureTemplate)
def post_stack_infrastructure_template(document: StackInfrastructureTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.put('', response_model=StackInfrastructureTemplate)
def put_stack_infrastructure_template(document: StackInfrastructureTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    producer.give_task_and_get_result(task)

    return document


@router.delete('/{name}', status_code=202)
def delete_stack_infrastructure_template(name: str):
    task = DocumentTask.parse_obj({
        'channel':
        'worker',
        'args': ("stack_infrastructure_template", name),
        'subtype':
        "DELETE_DOCUMENT"
    })

    result = producer.give_task_and_get_result(task)

    return result.return_result
