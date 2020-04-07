import logging

from fastapi import APIRouter, Query

from manager.manager_factory import ManagerFactory
from model.configs.policy_model import Policy
from model.configs.stack_application_template_model import StackApplicationTemplate
from model.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from opa_broker.opa_broker_factory import OPABrokerFactory

logger = logging.getLogger(__name__)
router = APIRouter()

opa_broker_factory = OPABrokerFactory()
opa_broker = opa_broker_factory.get_opa_broker()
document_manager = ManagerFactory().get_document_manager()

queries_for_sit_sats_set = Query("solution_set_per_service",
                                 enum=[
                                     "solution_set_per_service",
                                     "services_targets_resources_match",
                                     "services_target_resources_no_match"
                                 ])

@router.get('/query')
def run_query_for_sit_and_sat(
    sit_name: str = "stack_infrastructure_template_opa_test1",
    sat_name: str = "stack_application_template_opa_test1",
    query: str = queries_for_sit_sats_set):
    sit_doc = document_manager.get_stack_infrastructure_template(sit_name)
    sat_doc = document_manager.get_stack_application_template(sat_name)
    sit_as_opa_data = opa_broker.convert_sit_to_opa_data(sit_doc)
    sat_as_opa_data = opa_broker.convert_sat_to_opa_data(sat_doc)
    opa_data = {**sat_as_opa_data, **sit_as_opa_data}
    return opa_broker.ask_opa_policy_decision("orchestration", query, opa_data)


@router.get('/query/sit_data')
def get_sit_data_from_sit(
    sit_name: str = "stack_infrastructure_template_opa_test1"):
    sit_doc = document_manager.get_stack_infrastructure_template(sit_name)
    return opa_broker.convert_sit_to_opa_data(sit_doc)


@router.get('/query/sat_data')
def get_sat_data_from_sat(
    sat_name: str = "stack_application_template_opa_test1"):
    sat_doc = document_manager.get_stack_application_template(sat_name)
    return opa_broker.convert_sat_to_opa_data(sat_doc)


@router.get('/query/sit_policies')
def get_sit_policies_from_sit(
    sit_name: str = "stack_infrastructure_template_opa_test1"):
    sit_doc = document_manager.get_stack_infrastructure_template(sit_name)
    return opa_broker.convert_sit_to_opa_policies(sit_doc)


@router.get('/query/sat_policies')
def get_sat_policies_from_sat(
    sat_name: str = "stack_application_template_opa_test1"):
    sat_doc = document_manager.get_stack_application_template(sat_name)
    return opa_broker.convert_sat_to_opa_policies(sat_doc)


@router.get('/data')
def get_data(data_path: str = "default"):
    result = opa_broker.get_opa_data(data_path)
    return result


@router.put('/data')
def put_data(data: dict, data_path: str = "default"):
    result = opa_broker.load_opa_data(data, data_path)
    return result


@router.delete('/data')
def delete_data(data_path: str = "default"):
    result = opa_broker.load_opa_data(data_path)
    return result

@router.get('/all')
def get_policies():
    result = opa_broker.get_opa_policies()
    return result


@router.get('/policy')
def get_policy(policy_id: str = "default"):
    result = opa_broker.get_opa_policy(policy_id)
    return result


@router.delete('/policy')
def delete_policy(policy_id: str = "default"):
    result = opa_broker.delete_opa_policy(policy_id)
    return result


@router.put('/policy')
def put_policy(policy_doc: Policy):
    result = opa_broker.load_opa_policy(policy_doc)
    return result


@router.put('/sit')
def put_sit_policies(sit_doc: StackInfrastructureTemplate):
    ### WIP
    result = opa_broker.load_opa_policies_from_sit(sit_doc)
    return result


@router.put('/sat')
def put_sat_policies(sat_doc: StackApplicationTemplate):
    ### WIP
    result = opa_broker.load_opa_policies_from_sat(sat_doc)
    return result
