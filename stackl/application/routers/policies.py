import logging
from typing import List

from fastapi import APIRouter, HTTPException

from globals import document_types
from utils.general_utils import get_hostname
from model.configs.document import PolicyDocument

from opa_broker.opa_broker_factory import OPABrokerFactory

logger = logging.getLogger(__name__)
router = APIRouter()

opa_broker_factory = OPABrokerFactory()
opa_broker = opa_broker_factory.get_opa_broker()


@router.get('/data')
def get_data(data_path: str = "default"):
    result = opa_broker.get_opa_data(data_path)
    return result


@router.put('/data')
def put_data(data:dict, data_path: str = "default"):
    result = opa_broker.load_opa_data(data, data_path)
    return result


@router.delete('/data')
def delete_data(data_path: str = "default"):
    result = opa_broker.load_opa_data(data_path)
    return result

@router.get('')
def get_policies():
    result = opa_broker.get_opa_policies()
    return result


@router.get('/{policy_id}')
def get_policy(policy_id: str):
    result = opa_broker.get_opa_policy(policy_id)
    return result


@router.delete('/{policy_id}')
def delete_policy(policy_id: str):
    result = opa_broker.delete_opa_policy(policy_id)
    return result

@router.put('')
def put_policy(policy_doc: PolicyDocument):
    result = opa_broker.load_opa_policy(policy_doc)
    return result
