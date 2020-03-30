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
def get_configurator_file(state: str):
    """Returns a configurator statefile"""
    try:
        document = document_manager.get_configurator_file(state)
    except InvalidDocTypeError as e:
        raise HTTPException(status_code=StatusCode.BAD_REQUEST, detail=e.msg)

    if document == {}:
        raise HTTPException(status_code=StatusCode.NOT_FOUND, detail="No document with name " + state)
    logger.debug("[DocumentsByType GET] document(s): " + str(document))
    return document


@router.post('/{state}')
def post_configurator_file(state: str, body: Any = Body(...)):
    document = document_manager.write_configurator_file(state, body)
    return document


@router.delete('/{state}', status_code=200)
def delete_configurator_file(state: str):
    document_manager.delete_configurator_file(state)
    return {"message": "Deleted document"}
