import logging
from typing import List
from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.functional_requirement_model import FunctionalRequirement
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.stackl_exceptions import InvalidDocTypeError


logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()


document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('', response_model=List[FunctionalRequirement])
def get_functional_requirements():
    """Returns all functional requirements with a specific type"""
    try:
        documents = document_manager.get_document(type="functional_requirement")
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    return documents

@router.get('/{document_name}', response_model=FunctionalRequirement)
def get_functional_requirement_by_name(document_name: str):
    """Returns a functional requirement"""
    try:
        document = document_manager.get_functional_requirement(document_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND, detail="No document with name " + document_name)
    logger.debug(f"[DocumentsByType GET] document(s): {document}")
    return document

@router.post('', response_model=FunctionalRequirement)
def post_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    try:
        existing_document = document_manager.get_document(type=document.type, document_name=document.name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if existing_document:
        raise HTTPException(status_code=StatusCode.CONFLICT, detail="A document with this name for POST already exists")

    document = document_manager.write_functional_requirement(document)
    return document

@router.put('', response_model=FunctionalRequirement)
def put_functional_requirement(document: FunctionalRequirement):
    """Create the document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    document = document_manager.write_functional_requirement(document)
    return document

@router.delete('/{document_name}', status_code=202)
def delete_functional_requirement(type_name: str, document_name: str):
    document_manager.remove_document(type=type_name, document_name=document_name)
    return {"message": "Deleted document"}
