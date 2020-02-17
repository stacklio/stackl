from fastapi import APIRouter

from utils.general_utils import get_hostname

router = APIRouter()


@router.get('')
def get_hostname():
    """Returns hostname of the REST API instance"""
    return get_hostname()
