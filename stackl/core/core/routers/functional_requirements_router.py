"""
Endpoint for Functional Requirements
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager
from core.models.configs.functional_requirement_model import FunctionalRequirement

router = APIRouter()


@router.get('', response_model=List[FunctionalRequirement])
def get_functional_requirements(
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        "API COLLECT request with type_name 'policy_template'"
    )
    return document_manager.get_functional_requirements()


@router.get('/{name}', response_model=FunctionalRequirement)
def get_functional_requirement_by_name(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a functional requirement"""
    logger.info(
        f"API GET request for type 'policy_template' and document '{name}'"
    )
    functional_requirement = document_manager.get_functional_requirement(name)
    if not functional_requirement:
        raise HTTPException(status_code=404, detail="FR not found")
    return functional_requirement


@router.post('', response_model=FunctionalRequirement)
def post_functional_requirement(
        document: FunctionalRequirement,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {document}")
    document_manager.write_functional_requirement(document)
    return document


@router.put('', response_model=FunctionalRequirement)
def put_functional_requirement(
        document: FunctionalRequirement,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    document_manager.write_functional_requirement(document)
    return document


@router.delete('/{name}')
def delete_functional_requirement(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Delete a functional requirement by name"""
    logger.info(
        f"API Delete request for document '{name}'"
    )
    document_manager.delete_functional_requirement(name)
    return {"result": f"deleted functional requirement {name}"}
