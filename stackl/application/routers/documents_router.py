import logging

from fastapi import APIRouter, HTTPException, Request

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
async def collect_documents_by_type(type_name: str, name: str = ""):
    """Returns a collection of all the documents with the specific type and optionally containing the given name"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name '{type_name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, name),
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


@router.get('/{type_name}/{name}', response_model=BaseDocument)
async def get_document_by_type_and_name(type_name: str, name: str):
    """Returns a specific document with a type and name"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type '{type_name}' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, name),
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
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")

    task = DocumentTask({
        'channel': 'worker',
        'document': document.dict(),
        'subtype': "POST_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if result == StatusCode.BAD_REQUEST:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="BAD_REQUEST. Document already exists")
    return result
    # try:

    #     existing_document = document_manager.get_document(
    #         type=document.type, name=document.name)
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
async def put_document(document: BaseDocument, request: Request):
    """Update (or create) the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PutDocument] API PUT request with data: {document}")
    json_body = await request.json()
    logger.info(f"[PutDocument] API PUT request with request: {json_body}")

    task = DocumentTask({
        'channel': 'worker',
        'document': json_body,
        'subtype': "PUT_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    return result


@router.delete('/{type_name}/{name}')
async def delete_document(type_name: str, name: str):
    """Delete a specific document with a type and name"""
    logger.info(
        f"[DeleteDocument] API Delete request for type '{type_name}' and document '{name}'"
    )
    task = DocumentTask({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "DELETE_DOCUMENT"
    })

    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    return result
