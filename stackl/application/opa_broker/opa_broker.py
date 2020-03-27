import json
import logging

import requests

from model.configs.policy_model import Policy
from model.configs.stack_application_template_model import StackApplicationTemplate
from model.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from model.items.service_model import Service
from utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")


##TODO WIP!
class OPABroker:

    def __init__(self):
        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))

    def start(self):
        logger.debug("[OPABroker] Initialising OPABroker.")
        self.load_default_policies()

    def load_default_policies(self):
        pass
        # Note that the ordering of the policies is important
        # logger.debug("[OPABroker] load_default_policies.")
        # data = open('/app/opa_broker/opa_files/functions.rego', 'r').read()
        # response = requests.put(self.opa_host + "/v1/policies/default", data=data)

        # data = open('/app/opa_broker/opa_files/orchestration_default_policies.rego', 'r').read()
        # response = requests.put(self.opa_host + "/v1/policies/orchestration", data=data)
        # logger.debug("[OPABroker] load_default_policies. Response:{}".format(response))

    def ask_opa_policy_decision(self, policy_package="default", policy_rule="default", data={}):
        logger.debug(
            "[OPABroker] ask_opa_policy_decision. For policy_package '{0}' and policy_rule '{1}'' and data '{2}'".format(
                policy_package, policy_rule, data))

        # create input to hand to OPA
        input_dict = {
            "input": data
        }

        try:
            response = requests.post(self.opa_host + "/v1/data/" + policy_package + "/" + policy_rule,
                                     data=json.dumps(input_dict))
        except Exception as err:
            logger.debug("[OPABroker] ask_opa_policy_decision. error '{0}'".format(err))
            return {}
        if response.status_code >= 300:
            logger.debug("[OPABroker] ask_opa_policy_decision. Error checking policy, got status %s and message: %s" %
                         (response.status_code, response.text))
            return {}
        response_as_json = response.json()
        logger.debug("[OPABroker] ask_opa_policy_decision. response '{0}'".format(response_as_json))
        return response_as_json

    def get_opa_policies(self):
        logger.debug("[OPABroker] get_opa_policies.")
        response = requests.get(self.opa_host + "/v1/policies")
        result = response.json()
        logger.debug("[OPABroker] get_opa_policies. Result: {}".format(result))
        return result

    def get_opa_policy(self, policy_id):
        logger.debug("[OPABroker] get_opa_policy. For policy_id '{0}'".format(policy_id))
        response = requests.get(self.opa_host + "/v1/policies/" + policy_id)
        result = response.json()
        logger.debug("[OPABroker] get_opa_policy. Result: {}".format(result))
        return result

    def get_opa_data(self, data_path="default"):
        logger.debug("[OPABroker] get_opa_data. For path '{}'".format(data_path))
        response = requests.get(self.opa_host + "/v1/data/" + data_path)
        result = response.json()
        logger.debug("[OPABroker] get_opa_data. Result: {}".format(result))
        return result

    def load_opa_data(self, data, path="default"):
        logger.debug("[OPABroker] load_opa_data. For data '{0}' and path '{1}'".format(data, path))
        response = requests.put(self.opa_host + "/v1/data/" + path, data=json.dumps(data))
        logger.debug("[OPABroker] load_opa_data. Response: {}".format(response))

    def delete_opa_data(self, data_path="default"):
        logger.debug("[OPABroker] delete_opa_data. For path '{}'".format(data_path))
        response = requests.delete(self.opa_host + "/v1/data/" + data_path)
        result = response.json()
        logger.debug("[OPABroker] delete_opa_data. Result: {}".format(result))
        return result

    def load_opa_policy(self, policy_doc: Policy, policy_id="default"):
        logger.debug("[OPABroker] load_opa_policy.For policy_doc '{0}'".format(policy_doc))
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id, data=policy_doc.policy)
        logger.debug("[OPABroker] load_opa_policy. Response:{}".format(response))

    def load_opa_policies_from_sit(self, sit_doc: StackInfrastructureTemplate):
        logger.debug("[OPABroker] load_opa_policies_from_sit.For policy_doc '{0}'".format(sit_doc))
        policy_id = "sit_policies_" + sit_doc.name
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id, data={})
        logger.debug("[OPABroker] load_opa_policies_from_sit. Response:{}".format(response))

    def load_opa_policies_from_sat(self, sat_doc: StackApplicationTemplate):
        logger.debug("[OPABroker] load_opa_policies_from_sat.For policy_doc '{0}'".format(sat_doc))
        policy_id = "sat_policies_" + sat_doc.name
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id, data={})
        logger.debug("[OPABroker] load_opa_policies_from_sat. Response:{}".format(response))

    def delete_opa_policy(self, policy_id="default"):
        logger.debug("[OPABroker] delete_opa_policy. For policy_id '{0}'".format(policy_id))
        response = requests.delete(self.opa_host + "/v1/policies/" + policy_id)
        logger.debug("[OPABroker] delete_opa_policy. Response:{}".format(response))

    def convert_sit_to_opa_data(self, sit_doc: StackInfrastructureTemplate):
        logger.debug("[OPABroker] convert_sit_to_opa_data. For sit_doc '{0}'".format(sit_doc))
        sit_targets = sit_doc.infrastructure_capabilities.keys()
        targets_as_data = {}
        sit_as_opa_data = {"infrastructure_targets": targets_as_data}
        for target in sit_targets:
            target_data = {"resources": sit_doc.infrastructure_capabilities[target]["resources"],
                           "config": sit_doc.infrastructure_capabilities[target]["configs"]}
            targets_as_data[target] = target_data
        logger.debug("[OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{0}'".format(sit_as_opa_data))
        return sit_as_opa_data

    def convert_sat_to_opa_data(self, sat_doc: StackApplicationTemplate, services: [Service]):
        logger.debug("[OPABroker] convert_sat_to_opa_data. For sat_doc '{0}'".format(sat_doc))
        services_as_data = {}
        sat_as_opa_data = {"services": services_as_data}
        for service in services:
            service_data = {"functional_requirements": service.functional_requirements,
                            "resource_requirements": service.resource_requirements}
            services_as_data[service.name] = service_data
        logger.debug("[OPABroker] convert_sat_to_opa_data. sat_as_opa_data '{0}'".format(sat_as_opa_data))
        return sat_as_opa_data

    def convert_sit_to_opa_policies(self, sit_doc: StackInfrastructureTemplate):
        logger.debug("[OPABroker] convert_sit_to_opa_data. For sit_doc '{0}'".format(sit_doc))
        sit_targets = sit_doc.infrastructure_capabilities.keys()
        targets_as_data = []
        sit_as_opa_data = {"infrastructure_targets": targets_as_data}
        for target in sit_targets:
            target_data = {"id": target, "resources": sit_doc.infrastructure_capabilities[target]["resources"],
                           "config": sit_doc.infrastructure_capabilities[target]["configs"]}
            targets_as_data.append(target_data)
        logger.debug("[OPABroker] convert_sit_to_opa_data. sit_as_opa_data '{0}'".format(sit_as_opa_data))
        return sit_as_opa_data

    def convert_sat_to_opa_policies(self, sat_doc: StackApplicationTemplate):
        logger.debug("[OPABroker] convert_sat_to_opa_policies. For sat_doc '{0}'".format(sat_doc))
        sat_policies = sat_doc.policies
        # services_as_data = []
        # sat_as_opa_data = {"services": services_as_data}
        for policy in sat_policies:
            policy_doc = self.document_manager.get_policy(policy)
        #     service_data = {}
        #     service_data["id"] = service_doc.name
        #     service_data["functional_requirements"] = service_doc.functional_requirements
        #     service_data["resource_requirements"] = service_doc.resource_requirements
        #     services_as_data.append(service_data)
        # logger.debug("[OPABroker] convert_sat_to_opa_data. sat_as_opa_data '{0}'".format(sat_as_opa_data))
        # return sat_as_opa_data
