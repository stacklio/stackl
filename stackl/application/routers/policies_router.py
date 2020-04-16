import logging

from fastapi import APIRouter, HTTPException

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.policy_model import Policy
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger(__name__)
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()


@router.get('/{policy}', response_model=Policy)
def get_policy_by_name(policy_name: str):
    """Returns a policy"""
    try:
        document = document_manager.get_policy(policy_name)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND,
                            detail="No document with name " +
                            policy_name)
    logger.debug(f"[DocumentsByType GET] document(s): {document}")
    return document


@router.put('')
def put_policy(policy: Policy):
    result = document_manager.write_policy(policy)
    return result
