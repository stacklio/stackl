import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Body

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from utils.stackl_exceptions import InvalidDocTypeError

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()


@router.get('/{state}')
def get_terraform_statefile(state: str):
    """Returns a terraform statefile"""
    try:
        document = document_manager.get_terraform_statefile(state)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND, detail="No document with name " + state)
    logger.debug("[DocumentsByType GET] document(s): " + str(document))
    return document


@router.post('/{state}')
def post_terraform_statefile(state: str, body: Any = Body(...)):
    document = document_manager.write_terraform_statefile(state, body)
    return document


@router.delete('/{state}', status_code=200)
def delete_terraform_statefile(state: str):
    document_manager.delete_terraform_statefile(state)
    return {"message": "Deleted document"}
