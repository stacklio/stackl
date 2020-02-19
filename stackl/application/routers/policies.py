import logging
from typing import List

from fastapi import APIRouter, HTTPException

from globals import document_types
from utils.general_utils import get_hostname
from opa_broker.opa_broker_factory import OPABrokerFactory

logger = logging.getLogger(__name__)
router = APIRouter()

opa_broker_factory = OPABrokerFactory()
opa_broker = opa_broker_factory.get_opa_broker()


@router.get('/policies')
def get_active_policies():
    result = opa_broker.get_opa_policies()
    return result
