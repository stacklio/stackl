import json
import requests

import globals
import logging
from utils.general_utils import get_config_key

logger = logging.getLogger(__name__)

class OPABroker:

    def __init__(self):
        self.opa_host = "http://{}".format(get_config_key("OPA_HOST"))

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
        logger.debug("[OPABroker] get_opa_policies.")
        rsp = requests.get(self.opa_host + "/v1/policies", verify=False)
        result = rsp.json()
        logger.debug("[OPABroker] get_opa_policies. Result: {}".format(result))
        return result
