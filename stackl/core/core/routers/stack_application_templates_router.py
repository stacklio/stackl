"""
Endpoint for CRUD operations on Stack Application Templates
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager
from core.models.configs.stack_application_template_model import StackApplicationTemplate

router = APIRouter()


@router.get('', response_model=List[StackApplicationTemplate])
def get_stack_application_templates(
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        "GET request with type_name 'stack_application_templates'"
    )
    sats = document_manager.get_stack_application_templates()
    return sats


@router.get('/{name}', response_model=StackApplicationTemplate)
def get_stack_application_template_by_name(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a functional requirement"""
    logger.info(
        f"GET request for type 'stack_application_template' and document '{name}'"
    )
    sat = document_manager.get_stack_application_template(name)
    if not sat:
        raise HTTPException(status_code=404, detail="SAT not found")
    return sat


@router.post('', response_model=StackApplicationTemplate)
def post_stack_application_template(
        sat: StackApplicationTemplate,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {sat}")

    document_manager.write_stack_application_template(sat)

    return sat


@router.put('', response_model=StackApplicationTemplate)
def put_stack_application_template(
        sat: StackApplicationTemplate,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    document_manager.write_stack_application_template(sat)

    return sat


@router.delete('/{name}')
def delete_stack_application_template(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Delete a stack application template by name"""
    document_manager.delete_stack_application_template(name)
    return {"result": "Deleted SAT"}
