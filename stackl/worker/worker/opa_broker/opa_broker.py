import json
import logging

import requests

from stackl.models.configs.policy_template_model import PolicyTemplate
from stackl.models.configs.stack_application_template_model import StackApplicationTemplate
from stackl.models.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from stackl.models.items.service_model import Service
from stackl.utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")


##TODO WIP!
class OPABroker:
    def __init__(self):
        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))
        self.manager_factory = None
        self.document_manager = None

    def start(self, manager_factory):
        logger.debug("[OPABroker] Initialising OPABroker.")
        self.manager_factory = manager_factory
        self.document_manager = self.manager_factory.get_document_manager()

    def add_policy(self, policy_name, policy_data):
        response = requests.put(self.opa_host + "/v1/policies/" + policy_name,
                                data=policy_data)
        logger.debug(f"[OPABroker] add_policy. Response:{response}")

    def ask_opa_policy_decision(self,
                                policy_package="default",
                                policy_rule="default",
                                data=None):
        logger.debug(
            f"[OPABroker] ask_opa_policy_decision. For policy_package '{policy_package}' and policy_rule '{policy_rule}'' and data '{data}'"
        )
        # create input to hand to OPA
        input_dict = {"input": data}
        try:
            response = requests.post(self.opa_host + "/v1/data/" +
                                     policy_package + "/" + policy_rule,
                                     data=json.dumps(input_dict))
        except Exception as err:  #pylint: disable=broad-except
            logger.debug(f"[OPABroker] ask_opa_policy_decision. error '{err}'")
            return {}
        if response.status_code >= 300:
            logger.debug(
                f"[OPABroker] ask_opa_policy_decision. Error checking policy, got status {response.status_code} and message: {response.text}"
            )
            return {}
        response_as_json = response.json()
        logger.debug(
            f"[OPABroker] ask_opa_policy_decision. response: {response_as_json}"
        )
        return response_as_json

    def get_opa_policies(self):
        logger.debug("[OPABroker] get_opa_policies.")
        response = requests.get(self.opa_host + "/v1/policies")
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_policies. Result: {result}")
        return result

    def get_opa_policy(self, policy_id):
        logger.debug(
            f"[OPABroker] get_opa_policy. For policy_id '{policy_id}'")
        response = requests.get(self.opa_host + "/v1/policies/" + policy_id)
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_policy. Result: {result}")
        return result

    def get_opa_data(self, data_path="default"):
        logger.debug("[OPABroker] get_opa_data. For path '{data_path}'")
        response = requests.get(self.opa_host + "/v1/data/" + data_path)
        result = response.json()
        logger.debug(f"[OPABroker] get_opa_data. Result: {result}")
        return result

    def load_opa_data(self, data, path="default"):
        logger.debug(
            f"[OPABroker] load_opa_data. For data '{data}' and path '{path}'")
        response = requests.put(self.opa_host + "/v1/data/" + path,
                                data=json.dumps(data))
        logger.debug(f"[OPABroker] load_opa_data. Response: {response}")

    def delete_opa_data(self, data_path="default"):
        logger.debug(f"[OPABroker] delete_opa_data. For path '{data_path}'")
        response = requests.delete(self.opa_host + "/v1/data/" + data_path)
        result = response.json()
        logger.debug(f"[OPABroker] delete_opa_data. Result: {result}")
        return result

    def load_opa_policy(self, policy_doc: PolicyTemplate, policy_id="default"):
        logger.debug(
            f"[OPABroker] load_opa_policy.For policy_doc '{policy_doc}'")
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id,
                                data=policy_doc.policy)
        logger.debug(f"[OPABroker] load_opa_policy. Response:{response}")

    def load_opa_policies_from_sit(self, sit_doc: StackInfrastructureTemplate):
        logger.debug(
            f"[OPABroker] load_opa_policies_from_sit. For policy_doc '{sit_doc}'"
        )
        policy_id = "sit_policies_" + sit_doc.name
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id,
                                data={})
        logger.debug(
            f"[OPABroker] load_opa_policies_from_sit. Response: {response}")

    def load_opa_policies_from_sat(self, sat_doc: StackApplicationTemplate):
        logger.debug(
            f"[OPABroker] load_opa_policies_from_sat.For policy_doc '{sat_doc}'"
        )
        policy_id = "sat_policies_" + sat_doc.name
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id,
                                data={})
        logger.debug(
            f"[OPABroker] load_opa_policies_from_sat. Response: {response}")

    def delete_opa_policy(self, policy_id="default"):
        logger.debug(
            f"[OPABroker] delete_opa_policy. For policy_id '{policy_id}'")
        response = requests.delete(self.opa_host + "/v1/policies/" + policy_id)
        logger.debug(f"[OPABroker] delete_opa_policy. Response:{response}")

    def convert_sit_to_opa_data(self, sit_doc: StackInfrastructureTemplate):
        logger.debug(
            f"[OPABroker] convert_sit_to_opa_data. For sit_doc '{sit_doc}'")
        sit_targets = sit_doc.infrastructure_capabilities.keys()
        targets_as_data = {}
        sit_as_opa_data = {"infrastructure_targets": targets_as_data}
        for target in sit_targets:
            target_data = {
                "resources":
                sit_doc.infrastructure_capabilities[target]["resources"],
                "packages":
                sit_doc.infrastructure_capabilities[target]["packages"],
                "tags":
                sit_doc.infrastructure_capabilities[target]["tags"],
                "params":
                sit_doc.infrastructure_capabilities[target]
                ['provisioning_parameters']
            }
            targets_as_data[target] = target_data
        logger.debug(
            f"[OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{sit_as_opa_data}'"
        )
        return sit_as_opa_data

    def convert_sat_to_opa_data(self, sat_doc: StackApplicationTemplate,
                                services: [Service]):
        logger.debug(
            f"[OPABroker] convert_sat_to_opa_data. For sat_doc '{sat_doc}'")
        services_as_data = {}
        sat_as_opa_data = {"services": services_as_data}
        for service in services:
            frs = {}
            params = service.params
            for fr in service.functional_requirements:
                fr_doc = self.document_manager.get_functional_requirement(fr)
                frs[fr] = fr_doc.invocation.dict()
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

    def convert_sat_to_opa_policies(self, sat_doc: StackApplicationTemplate):
        logger.debug(
            f"[OPABroker] convert_sat_to_opa_policies. For sat_doc '{sat_doc}'"
        )
        sat_policies = sat_doc.policies
        # services_as_data = []
        # sat_as_opa_data = {"services": services_as_data}
        for policy in sat_policies:
            policy_doc = self.document_manager.get_policy_template(policy)
        #     service_data = {}
        #     service_data["id"] = service_doc.name
        #     service_data["functional_requirements"] = service_doc.functional_requirements
        #     service_data["resource_requirements"] = service_doc.resource_requirements
        #     services_as_data.append(service_data)
        # logger.debug("[OPABroker] convert_sat_to_opa_data. sat_as_opa_data '{0}'".format(sat_as_opa_data))
        # return sat_as_opa_data

    def convert_sit_to_opa_policies(self,
                                    sit_doc: StackInfrastructureTemplate):
        logger.debug(
            f"[OPABroker] convert_sit_to_opa_data. For sit_doc '{sit_doc}'")
        sit_targets = sit_doc.infrastructure_capabilities.keys()
        targets_as_data = []
        sit_as_opa_data = {"infrastructure_targets": targets_as_data}
        for target in sit_targets:
            target_data = {
                "id":
                target,
                "resources":
                sit_doc.infrastructure_capabilities[target]["resources"],
                "packages":
                sit_doc.infrastructure_capabilities[target]["packages"]
            }
            targets_as_data.append(target_data)
        logger.debug(
            f"[OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{sit_as_opa_data}'"
        )
        return sit_as_opa_data
