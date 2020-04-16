import logging

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.policy_template_model import PolicyTemplate
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger(__name__)
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()

@router.get('/{policy}', response_model=PolicyTemplate)
def get_policy_template_by_name(policy_template_name: str):
    """Returns a policy"""
    try:
        document = document_manager.get_policy_template(policy_template_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail="No document with name " +
                            policy_template_name)
    logger.debug(f"[DocumentsByType GET] document(s): {document}")
    return document

@router.put('/policy')
def put_policy_template(policy_template: PolicyTemplate):
    result = document_manager.write_policy_template(policy_template)
    return result
