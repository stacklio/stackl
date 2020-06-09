import logging

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.infrastructure_base_document import InfrastructureBaseDocument
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()


@router.get('/{infrastructure_base_type}',
            response_model=InfrastructureBaseDocument)
def get_infrastructure_base_by_type(infrastructure_base_type: str):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        f"[InfrastructureBaseByTypeAndName GET] Receiver GET request with data: {infrastructure_base_type}"
    )
    try:
        document = document_manager.get_document(type=infrastructure_base_type,
                                                 category="configs")
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    logger.debug(
        f"[InfrastructureBaseByTypeAndName GET] document(s): {document}")
    return document


@router.get('/{infrastructure_base_type}/{infrastructure_base_name}',
            response_model=InfrastructureBaseDocument)
def get_infrastructure_base_by_type_and_name(infrastructure_base_type: str,
                                             infrastructure_base_name: str):
    """Returns a specific infrastructure_base document with a type and name"""
    logger.info(
        "[InfrastructureBaseByTypeAndName GET] Receiver GET request with data: "
        + infrastructure_base_type + " - " + infrastructure_base_name)
    try:
        document = document_manager.get_document(
            type=infrastructure_base_type,
            document_name=infrastructure_base_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail="No document with name " +
                            infrastructure_base_name)
    logger.debug(
        f"[InfrastructureBaseByTypeAndName GET] document(s): {document}")
    return document


@router.post('', response_model=InfrastructureBaseDocument)
def post_infrastructure_base(
    infrastructure_base_doc: InfrastructureBaseDocument):
    """Create the infrastructure_base document with a specific type and an optional name given in the payload"""
    # check if doc already exists
    try:
        existing_infrastructure_base_document = document_manager.get_document(
            type=infrastructure_base_doc.type,
            document_name=infrastructure_base_doc.name)
    except InvalidDocTypeError as e:
        return {
            'return_code': StatusCode.BAD_REQUEST,
            'message': e.msg
        }, StatusCode.BAD_REQUEST

    if existing_infrastructure_base_document:
        raise HTTPException(
            status_code=StatusCode.CONFLICT,
            detail="A document with this name for POST already exists")

    document = document_manager.write_base_document(infrastructure_base_doc)
    return document


@router.put('', response_model=InfrastructureBaseDocument)
def put_infrastructure_base(
    infrastructure_base_document: InfrastructureBaseDocument):
    """UPDATES the infrastructure_base document with a specific type and an optional name given in the payload"""
    document = document_manager.write_base_document(
        infrastructure_base_document)
    return document


@router.delete('/{infrastructure_base_type}/{infrastructure_base_name}',
               status_code=202)
def delete_infrastructure_base(infrastructure_base_type: str,
                               infrastructure_base_name: str):
    document_manager.remove_document(type=infrastructure_base_type,
                                     document_name=infrastructure_base_name)
    return {"message": "Deleted infrastructure_base_document"}
