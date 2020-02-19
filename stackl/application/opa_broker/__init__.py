import json
import requests

import globals
import logging
from utils.general_utils import get_config_key

logger = logging.getLogger(__name__)

class OPABroker:

    def __init__(self):
        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))
        self.load_default_policies()

    def load_default_policies(self):
        logger.info("[OPABroker] load_default_policies.")
        # data = open('stackl_default_policies.rego', 'rb').read()
        # response = requests.put('http://localhost:8181/v1/policies/example', data=data)
        # logger.debug("[OPABroker] load_default_policies. Response:{}".format(response))


    def create_opa_input(self, input):
        input_dict = {  # create input to hand to OPA
            "input": {
                "user": "test",
                "path": "test",  
                "method": "test" 
            }
        }
        return input_dict

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
        logger.info("[OPABroker] get_opa_policies.")
        response = requests.get(self.opa_host + "/v1/policies", verify=False)
        result = response.json()
        logger.debug("[OPABroker] get_opa_policies. Result: {}".format(result))
        return result
