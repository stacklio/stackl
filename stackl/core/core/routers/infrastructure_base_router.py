import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from core.models.configs.infrastructure_base_document import InfrastructureBaseDocument

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager

from loguru import logger
router = APIRouter()


@router.get('/{infrastructure_base_type}',
            response_model=List[InfrastructureBaseDocument])
def get_infrastructure_base_by_type(
    infrastructure_base_type: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name '{infrastructure_base_type}'"
    )
    if infrastructure_base_type == "environment":
        infrastructure_documents = document_manager.get_environments()
    elif infrastructure_base_type == "location":
        infrastructure_documents = document_manager.get_locations()
    elif infrastructure_base_type == "zone":
        infrastructure_documents = document_manager.get_zones()
    else:
        raise HTTPException(
            status_code=400,
            detail="type has to be environment, location or zone")

    return infrastructure_documents


@router.get('/{infrastructure_base_type}/{infrastructure_base_name}',
            response_model=InfrastructureBaseDocument)
def get_infrastructure_base_by_type_and_name(
    infrastructure_base_type: str,
    infrastructure_base_name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type '{infrastructure_base_type}' and document '{infrastructure_base_name}'"
    )
    if infrastructure_base_type == "environment":
        infrastructure_document = document_manager.get_environment(
            infrastructure_base_name)
    elif infrastructure_base_type == "location":
        infrastructure_document = document_manager.get_location(
            infrastructure_base_name)
    elif infrastructure_base_type == "zone":
        infrastructure_document = document_manager.get_zone(
            infrastructure_base_name)
    else:
        raise HTTPException(
            status_code=400,
            detail="type has to be environment, location or zone")

    if not infrastructure_document:
        raise HTTPException(status_code=404, detail="Document not found")

    return infrastructure_document


@router.post('', response_model=InfrastructureBaseDocument)
def post_infrastructure_base(
    infrastructure_base_document: InfrastructureBaseDocument,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the infrastructure_base document with a specific type and an optional name given in the payload"""
    logger.info(
        f"[PostDocument] Receiver POST request with data: {infrastructure_base_document}"
    )

    infrastructure_document = document_manager.write_base_document(
        infrastructure_base_document)

    return infrastructure_document


@router.put('', response_model=InfrastructureBaseDocument)
def put_infrastructure_base(
    infrastructure_base_document: InfrastructureBaseDocument,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """UPDATES the infrastructure_base document with a specific type and an optional name given in the payload"""
    infrastructure_document = document_manager.write_base_document(
        infrastructure_base_document)

    return infrastructure_document


@router.delete('/{infrastructure_base_type}/{infrastructure_base_name}',
               status_code=200)
def delete_infrastructure_base(
    infrastructure_base_type: str,
    infrastructure_base_name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    document_manager.delete_base_document(infrastructure_base_type,
                                          infrastructure_base_name)

    return {
        "result":
        f"deleted {infrastructure_base_type} {infrastructure_base_name}"
    }
