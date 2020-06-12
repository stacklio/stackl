import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.stack_application_template_model import StackApplicationTemplate
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.document_task import DocumentTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[StackApplicationTemplate])
def get_stack_application_templates():
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'stack_application_templates'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': "stack_application_template",
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.get('/{name}', response_model=StackApplicationTemplate)
def get_stack_application_template_by_name(name: str):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'stack_application_template' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': ('stack_application_template', name),
        'subtype': "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.post('', response_model=StackApplicationTemplate)
def post_stack_application_template(document: StackApplicationTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.put('', response_model=StackApplicationTemplate)
def put_stack_application_template(document: StackApplicationTemplate):
    """Create the document with a specific type and an optional name given in the payload"""
    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.delete('/{name}', status_code=202)
def delete_stack_application_template(name: str):
    task = DocumentTask({
        'channel': 'worker',
        'args': ("stack_application_template", name),
        'subtype': "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result
