import json
import requests
import os

import globals
import logging
from utils.general_utils import get_config_key
from model.configs.stack_application_template import StackApplicationTemplate
from model.configs.stack_infrastructure_template import StackInfrastructureTemplate

from model.configs.document import PolicyDocument

logger = logging.getLogger("STACKL_LOGGER")

class OPABroker():

    def __init__(self):
        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))

    def start(self):
        logger.debug("[OPABroker] Initialising OPABroker.")

        self.load_default_policies()
        # self.load_default_data()

    def load_default_policies(self):
        logger.debug("[OPABroker] load_default_policies.")
        data = open('/app/opa_broker/opa_files/stackl_default_orchestration_policies.rego', 'r').read()
        response = requests.put(self.opa_host + "/v1/policies/stackl_orchestration_policies", data=data)
        logger.debug("[OPABroker] load_default_policies. Response:{}".format(response))

    # def load_default_data(self):
    #     logger.debug("[OPABroker] load_default_data.")
    #     data = self.create_opa_input_data()
    #     self.load_opa_data(data)

    # def create_opa_input_data(self, input=None):
    #     if input:
    #         return input
    #     else:
    #         return {  # create input to hand to OPA
    #             "input": {
    #                 "user": "test",
    #                 "path": "test",  
    #                 "method": "test2" 
    #             }
    #     }

    def ask_opa_policy_decision(self):
        # rsp = requests.post
        # if rsp.json()["allow"]:
        #     pass
        #   # HTTP API allowed
        # else:
        #   # HTTP API denied
        #     pass
        pass

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

    def load_opa_policy(self, policy_doc: PolicyDocument, policy_id="default"):
        logger.debug("[OPABroker] load_opa_policy.For policy_doc '{0}'".format(policy_doc))
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id, data=policy_doc.policy)
        logger.debug("[OPABroker] load_opa_policy. Response:{}".format(response))

    def load_opa_policies_from_sit(self, sit_doc: StackInfrastructureTemplate):
        logger.debug("[OPABroker] load_opa_policies_from_sit.For policy_doc '{0}'".format(sit_doc))
        policy_id = "sit_policies_" + sit_doc.name
        response = requests.put(self.opa_host + "/v1/policies/" + policy_id, data= {})
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
