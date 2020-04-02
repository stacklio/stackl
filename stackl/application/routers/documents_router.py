import logging
from typing import List
from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from stackl_globals import types
from manager.manager_factory import ManagerFactory
from model.configs.document_model import BaseDocument
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('/types')
def get_types():
    return types


@router.get('/{type_name}', response_model=List[BaseDocument])
def get_documents_by_type(type_name: str):
    """Returns all documents with a specific type"""
    logger.info(
        f"[DocumentsByType GET] Receiver GET request with data: {type_name}")
    try:
        documents = document_manager.get_document(type=type_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    logger.debug(f"[DocumentsByType GET] document(s): {documents}")
    return documents


@router.get('/{type_name}/{document_name}', response_model=BaseDocument)
def get_document_by_type_and_name(type_name: str, document_name: str):
    """Returns a specific document with a type and name"""
    logger.info(
        "[DocumentByTypeAndName GET] Receiver GET request with data: " +
        type_name + " - " + document_name)
    try:
        document = document_manager.get_document(type=type_name,
                                                 document_name=document_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail="No document with name " + document_name)
    logger.debug(f"[DocumentsByType GET] document(s): {document}")
    return document


@router.post('', response_model=BaseDocument)
def post_document(document: BaseDocument):
    """Create the document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    try:
        existing_document = document_manager.get_document(
            type=document.type, document_name=document.name)
    except InvalidDocTypeError as e:
        return {
            'return_code': StatusCode.BAD_REQUEST,
            'message': e.msg
        }, StatusCode.BAD_REQUEST

    if existing_document:
        raise HTTPException(
            status_code=StatusCode.CONFLICT,
            detail="A document with this name for POST already exists")

    document = document_manager.write_base_document(document)
    return document


@router.put('', response_model=BaseDocument)
def put_document(document: BaseDocument):
    """UPDATES the document with a specific type and an optional name given in the payload"""
    document = document_manager.write_base_document(document)
    return document


@router.delete('/{type_name}/{document_name}', status_code=202)
def delete_document(type_name: str, document_name: str):
    document_manager.remove_document(type=type_name,
                                     document_name=document_name)
    return {"message": "Deleted document"}
