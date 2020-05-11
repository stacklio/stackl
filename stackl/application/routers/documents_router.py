import logging

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.document_model import BaseDocument, CollectionDocument
from stackl_globals import types
from task_broker.task_broker_factory import TaskBrokerFactory
from task.document_task import DocumentTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('/types')
def get_types():
    return types


@router.get('/{type_name}', response_model=CollectionDocument)
async def collect_documents_by_type(type_name: str):
    """Returns a collection of all the documents with the specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name '{type_name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': type_name,
        'subtype': "COLLECT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    document: CollectionDocument = {
        "name": "CollectionDocumentByType_" + type_name,
        "description":
        "Document that contains all the documents by type " + type_name,
        "type": type_name,
        "documents": result
    }
    return document


@router.get('/{type_name}/{document_name}', response_model=BaseDocument)
async def get_document_by_type_and_name(type_name: str, document_name: str):
    """Returns a specific document with a type and name"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type '{type_name}' and document '{document_name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, document_name),
        'subtype': "GET_DOCUMENT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    if result == {}:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result


@router.post('')
async def post_document(document: BaseDocument):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(
        f"[PostDocument] Receiver POST request with data: {BaseDocument}")

    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if result == {}:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result
    # try:

    #     existing_document = document_manager.get_document(
    #         type=document.type, document_name=document.name)
    # except InvalidDocTypeError as e:
    #     return {
    #         'return_code': StatusCode.BAD_REQUEST,
    #         'message': e.msg
    #     }, StatusCode.BAD_REQUEST

    # if existing_document:
    #     raise HTTPException(
    #         status_code=StatusCode.CONFLICT,
    #         detail="A document with this name for POST already exists")

    # document = document_manager.write_base_document(document)
    # return document


@router.put('')
async def put_document(document: BaseDocument):
    """Update (or create) the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PutDocument] API PUT request with data: {BaseDocument}")

    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    return result


@router.delete('/{type_name}/{document_name}')
async def delete_document(type_name: str, document_name: str):
    """Delete a specific document with a type and name"""
    logger.info(
        f"[DeleteDocument] API Delete request for type '{type_name}' and document '{document_name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, document_name),
        'subtype': "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    return result
