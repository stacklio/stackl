import logging
from typing import List

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.policy_template_model import PolicyTemplate
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger(__name__)
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()


@router.get('', response_model=List[PolicyTemplate])
def get_policy_templates():
    """Returns all functional requirements with a specific type"""
    try:
        documents = document_manager.get_document(type="policy_template")
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    return documents


@router.get('/{policy_name}', response_model=PolicyTemplate)
def get_policy_template_by_name(policy_name: str):
    """Returns a policy template"""
    try:
        document = document_manager.get_policy_template(policy_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail="No document with name " + policy_name)
    logger.debug(f"[DocumentsByType GET] document(s): {document}")
    return document


@router.put('')
def put_policy_template(policy: PolicyTemplate):
    result = document_manager.write_policy_template(policy)
    return result
