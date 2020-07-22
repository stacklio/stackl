from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from core.models.items.service_model import Service

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager

router = APIRouter()


@router.get('', response_model=List[Service])
def get_services(
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'service'"
    )
    services = document_manager.get_services()
    return services


@router.get('/{name}', response_model=Service)
def get_service_by_name(
    name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a functional requirement"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'service' and document '{name}'"
    )
    service = document_manager.get_service(name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post('', response_model=Service)
def post_service(
    service: Service,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    logger.info(f"[PostDocument] Receiver POST request with data: {service}")

    document_manager.write_service(service)
    return service


@router.put('', response_model=Service)
def put_service(
    service: Service,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Create the document with a specific type and an optional name given in the payload"""
    document_manager.write_service(service)
    return service


@router.delete('/{name}', status_code=200)
def delete_service(
    name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    document_manager.delete_service(name)
    return {"result": "deleted service"}
