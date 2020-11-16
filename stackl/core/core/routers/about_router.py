"""
Endpoint for retrieving metadata from Stackl
"""

from fastapi import APIRouter

from core.utils.general_utils import get_hostname as utils_hostname

router = APIRouter()


@router.get('')
def get_hostname():
    """Returns hostname of the REST API instance"""
    return utils_hostname()
