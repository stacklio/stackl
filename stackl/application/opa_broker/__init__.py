import json
import requests
import os

import globals
import logging
from utils.general_utils import get_config_key

logger = logging.getLogger("STACKL_LOGGER")

class OPABroker():

    def __init__(self):
        pass

    def start(self):
        logger.debug("[OPABroker] Initialising OPABroker.")

        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))
        self.load_default_policies()
        self.load_default_data()

    def load_default_policies(self):
        logger.debug("[OPABroker] load_default_policies.")
        data = open('/app/opa_broker/stackl_default_policies.rego', 'rb').read()
        response = requests.put(self.opa_host + "/v1/policies/example", data=data)
        logger.debug("[OPABroker] load_default_policies. Response:{}".format(response))

    def load_default_data(self):
        logger.debug("[OPABroker] load_default_data.")
        data = self.create_opa_input_data()
        self.load_opa_data(data, "default")

    def create_opa_input_data(self, input=None):
        if input:
            return input
        else:
            return {  # create input to hand to OPA
                "input": {
                    "user": "test",
                    "path": "test",  
                    "method": "test2" 
                }
        }

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

    def get_opa_data(self, path = "current"):
        logger.debug("[OPABroker] get_opa_data for path '{}'".format(path))
        response = requests.get(self.opa_host + "/v1/data/"  + path)
        result = response.json()
        logger.debug("[OPABroker] get_opa_data. Result: {}".format(result))
        return result

    def load_opa_data(self, data, path="current"):
        logger.debug("[OPABroker] load_opa_data for data '{0}' and path '{1}'".format(data, path))
        response = requests.put(self.opa_host + "/v1/data/" + path, data=json.dumps(data))
        logger.debug("[OPABroker] load_opa_data. response: {}".format(response))
