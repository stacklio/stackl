import logging
from typing import List

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.items.service_model import Service
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[Service])
def get_services():
    """Returns all functional requirements with a specific type"""
    try:
        documents = document_manager.get_document(type="service")
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    return documents


@router.get('/{document_name}', response_model=Service)
def get_service_by_name(document_name: str):
    """Returns a functional requirement"""
    try:
        document = document_manager.get_service(document_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND, detail="No document with name " + document_name)
    logger.debug("[DocumentsByType GET] document(s): " + str(document))
    return document


@router.post('', response_model=Service)
def post_service(document: Service):
    """Create the document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    try:
        existing_document = document_manager.get_document(type=document.type, document_name=document.name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if existing_document:
        raise HTTPException(status_code=StatusCode.CONFLICT, detail="A document with this name for POST already exists")

    document = document_manager.write_service(document)
    return document


@router.put('', response_model=Service)
def put_service(document: Service):
    """Create the document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    document = document_manager.write_service(document)
    return document


@router.delete('/{document_name}', status_code=202)
def delete_service(type_name: str, document_name: str):
    document_manager.remove_document(type=type_name, document_name=document_name)
    return {"message": "Deleted document"}
