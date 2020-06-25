import logging
from typing import List

from fastapi import APIRouter
from stackl.models.configs.infrastructure_base_document import InfrastructureBaseDocument
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.document_task import DocumentTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

task_broker = TaskBrokerFactory().get_task_broker()


@router.get('/{infrastructure_base_type}',
            response_model=List[InfrastructureBaseDocument])
def get_infrastructure_base_by_type(infrastructure_base_type: str):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name '{infrastructure_base_type}'"
    )
    task = DocumentTask.parse_obj({
        'channel': 'worker',
        'args': infrastructure_base_type,
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.get('/{infrastructure_base_type}/{infrastructure_base_name}',
            response_model=InfrastructureBaseDocument)
def get_infrastructure_base_by_type_and_name(infrastructure_base_type: str,
                                             infrastructure_base_name: str):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type '{infrastructure_base_type}' and document '{infrastructure_base_name}'"
    )
    task = DocumentTask.parse_obj({
        'channel':
        'worker',
        'args': (infrastructure_base_type, infrastructure_base_name),
        'subtype':
        "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.post('', response_model=InfrastructureBaseDocument)
def post_infrastructure_base(
    infrastructure_base_document: InfrastructureBaseDocument):
    """Create the infrastructure_base document with a specific type and an optional name given in the payload"""
    logger.info(
        f"[PostDocument] Receiver POST request with data: {infrastructure_base_document}"
    )

    task = DocumentTask.parse_obj({
        'channel':
        'worker',
        'document':
        infrastructure_base_document.dict(),
        'subtype':
        "POST_DOCUMENT"
    })

    task_broker.give_task(task)
    task_broker.get_task_result(task.id)

    return infrastructure_base_document


@router.put('', response_model=InfrastructureBaseDocument)
def put_infrastructure_base(
    infrastructure_base_document: InfrastructureBaseDocument):
    """UPDATES the infrastructure_base document with a specific type and an optional name given in the payload"""
    task = DocumentTask.parse_obj({
        'channel':
        'worker',
        'document':
        infrastructure_base_document.dict(),
        'subtype':
        "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    task_broker.get_task_result(task.id)

    return infrastructure_base_document


@router.delete('/{infrastructure_base_type}/{infrastructure_base_name}',
               status_code=202)
def delete_infrastructure_base(infrastructure_base_type: str,
                               infrastructure_base_name: str):
    task = DocumentTask.parse_obj({
        'channel':
        'worker',
        'args': (infrastructure_base_type, infrastructure_base_name),
        'subtype':
        "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result
