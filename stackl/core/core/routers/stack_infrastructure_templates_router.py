from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from core.models.configs.stack_infrastructure_template_model import StackInfrastructureTemplate

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager

router = APIRouter()


@router.get('', response_model=List[StackInfrastructureTemplate])
def get_stack_infrastructure_templates(
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'stack_infrastructrure_templates'"
    )
    return document_manager.get_stack_infrastructure_templates()


@router.get('/{name}', response_model=StackInfrastructureTemplate)
def get_stack_infrastructure_template_by_name(
    name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'stack_infrastructure_template' and document '{name}'"
    )
    sit = document_manager.get_stack_infrastructure_template(name)
    if not sit:
        raise HTTPException(status_code=404, detail="SIT not found")
    return sit


@router.post('', response_model=StackInfrastructureTemplate)
def post_stack_infrastructure_template(
    sit: StackInfrastructureTemplate,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {sit}")

    document_manager.write_stack_infrastructure_template(sit)
    return sit


@router.put('', response_model=StackInfrastructureTemplate)
def put_stack_infrastructure_template(
    sit: StackInfrastructureTemplate,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    document_manager.write_stack_infrastructure_template(sit)
    return sit


@router.delete('/{name}')
def delete_stack_infrastructure_template(
    name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    document_manager.delete_stack_infrastructure_template(name)
    return {"result": "Deleted sit"}
