"""
Endpoint for CRUD operations on policy templates
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from core.manager.document_manager import DocumentManager
from core.manager.stackl_manager import get_document_manager
from core.models.configs.policy_template_model import PolicyTemplate

router = APIRouter()


@router.get('', response_model=List[PolicyTemplate])
def get_policy_templates(
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns all functional requirements with a specific type"""
    logger.info(
        "GET request with type_name 'policy_template'"
    )
    policy_templates = document_manager.get_policy_templates()
    return policy_templates


@router.get('/{policy_name}', response_model=PolicyTemplate)
def get_policy_template_by_name(
        policy_name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """Returns a policy template"""
    logger.info(
        f"GET request for type 'policy_template' and document '{policy_name}'"
    )
    policy_template = document_manager.get_policy_template(policy_name)
    if not policy_template:
        raise HTTPException(status_code=404,
                            detail="Policy template not found")
    return policy_template


@router.put('', response_model=PolicyTemplate)
def put_policy_template(
        policy: PolicyTemplate,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """
    Updates a policy template
    """
    logger.info(
        f"[PutDocument] API PUT request with policy_template: {policy}")
    policy_template = document_manager.write_policy_template(policy)
    return policy_template


@router.delete('/{name}', status_code=200)
def delete_policy_template(
        name: str,
        document_manager: DocumentManager = Depends(get_document_manager)):
    """
    Deletes a policy template by name
    """
    document_manager.delete_policy_template(name)
    return {"result": "deleted policy template"}
