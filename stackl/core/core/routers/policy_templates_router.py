from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from stackl.models.configs.policy_template_model import PolicyTemplate

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager

router = APIRouter()


@router.get('', response_model=List[PolicyTemplate])
def get_policy_templates(
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        f"[CollectionDocumentByType GET] API COLLECT request with type_name 'policy_template'"
    )
    policy_templates = document_manager.get_policy_templates()
    return policy_templates


@router.get('/{policy_name}', response_model=PolicyTemplate)
def get_policy_template_by_name(
    policy_name: str,
    document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a policy template"""
    logger.info(
        f"[DocumentByTypeAndName GET] API GET request for type 'policy_template' and document '{policy_name}'"
    )
    policy_template = document_manager.get_policy_template(policy_name)
    return policy_template


@router.put('')
def put_policy_template(
    policy: PolicyTemplate,
    document_manager: DocumentManager = Depends(get_document_manager)):
    logger.info(
        f"[PutDocument] API PUT request with policy_template: {policy}")
    policy_template = document_manager.write_policy_template(policy)
    return policy_template