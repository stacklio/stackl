"""Module containing all methods for interacting with OPA"""

import json
from typing import List

import requests
from loguru import logger

from core import config
from core.models.configs.stack_application_template_model import \
    StackApplicationTemplate
from core.models.configs.stack_infrastructure_template_model import \
    StackInfrastructureTemplate
from core.models.items.service_model import Service


def convert_sit_to_opa_data(sit_doc: StackInfrastructureTemplate):
    """Converts SIT to data for OPA policy evaluation"""
    logger.debug(
        f"[OPABroker] convert_sit_to_opa_data. For sit_doc '{sit_doc}'")
    sit_targets = sit_doc.infrastructure_capabilities.keys()
    targets_as_data = {}
    sit_as_opa_data = {"infrastructure_targets": targets_as_data}
    for target in sit_targets:
        target_data = {
            "resources":
            sit_doc.infrastructure_capabilities[target].resources,
            "packages":
            sit_doc.infrastructure_capabilities[target].packages,
            "tags":
            sit_doc.infrastructure_capabilities[target].tags,
            "params":
            sit_doc.infrastructure_capabilities[target].provisioning_parameters
        }
        targets_as_data[target] = target_data
    logger.debug(
        f"[OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{sit_as_opa_data}'"
    )
    return sit_as_opa_data


class OPABroker:
    """Class responsible for all communication between Stackl and OPA"""
    def __init__(self):
        self.opa_host = config.settings.stackl_opa_host
        self.manager_factory = None
        self.document_manager = None

    def start(self, manager_factory):
        """Starts the OPA Broker"""
        logger.debug("Initialising OPABroker.")
        self.manager_factory = manager_factory
        self.document_manager = self.manager_factory.get_document_manager()

    def add_policy(self, policy_name, policy_data):
        """Adds a policy in OPA"""
        response = requests.put(self.opa_host + "/v1/policies/" + policy_name,
                                data=policy_data)
        logger.debug(f"Response:{response}")

    def ask_opa_policy_decision(self,
                                policy_package="default",
                                policy_rule="default",
                                data=None):
        """Asks for a policy evaluation and returns result"""
        logger.debug(
            f"For policy_package '{policy_package}' and policy_rule '{policy_rule}' \
            and data '{json.dumps(data)}'")
        # create input to hand to OPA
        input_dict = {"input": data}
        try:
            response = requests.post(self.opa_host + "/v1/data/" +
                                     policy_package + "/" + policy_rule,
                                     data=json.dumps(input_dict))
        except Exception as err:  # pylint: disable=broad-except
            logger.debug(f"[OPABroker] ask_opa_policy_decision. error '{err}'")
            return {}
        if response.status_code >= 300:
            logger.debug(
                f"Error checking policy, status: {response.status_code} message: {response.text}"
            )
            return {}
        response_as_json = response.json()
        logger.debug(f"response: {response_as_json}")
        return response_as_json

    def get_opa_policies(self):
        """Return all policies available in OPA"""
        logger.debug("[OPABroker] get_opa_policies.")
        response = requests.get(self.opa_host + "/v1/policies")
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_policies. Result: {result}")
        return result

    def get_opa_policy(self, policy_id):
        """Returns a specific policy from OPA by ID"""
        logger.debug(
            f"[OPABroker] get_opa_policy. For policy_id '{policy_id}'")
        response = requests.get(self.opa_host + "/v1/policies/" + policy_id)
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_policy. Result: {result}")
        return result

    def get_opa_data(self, data_path="default"):
        """Retrieve data from OPA"""
        logger.debug("[OPABroker] get_opa_data. For path '{data_path}'")
        response = requests.get(self.opa_host + "/v1/data/" + data_path)
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_data. Result: {result}")
        return result

    def convert_sat_to_opa_data(self, sat_doc: StackApplicationTemplate,
                                services: List[Service]):
        """Converts SAT to data for OPA policy evaluation"""
        logger.debug(
            f"[OPABroker] convert_sat_to_opa_data. For sat_doc '{sat_doc}'")
        services_as_data = {}
        sat_as_opa_data = {"services": services_as_data}
        for service in services:
            frs = {}
            params = service.params
            for fr in service.functional_requirements:
                fr_doc = self.document_manager.get_functional_requirement(fr)
                frs[fr] = {
                    key: value.dict()
                    for (key, value) in fr_doc.invocation.items()
                }
                params = {**params, **fr_doc.params}
            service_data = {
                "functional_requirements": frs,
                "resource_requirements": service.resource_requirements,
                "params": params
            }
            services_as_data[service.name] = service_data
        logger.debug(
            f"[OPABroker] convert_sat_to_opa_data. sat_as_opa_data '{sat_as_opa_data}'"
        )
        return sat_as_opa_data
