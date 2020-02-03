import sys


from logger import Logger
from utils.stackl_singleton import Singleton
from utils.general_utils import get_config_key

class AgentBrokerFactory(metaclass=Singleton):

    def __init__(self):
        self.agent_broker_type = get_config_key('AGENT_BROKER')
        self.logger = Logger("AgentBrokerFactory")
        self.logger.info("[AgentBrokerFactory] Creating Agent Broker with type: " + self.agent_broker_type)
        self.agent_broker = None

        if self.agent_broker_type == "gitlab-runner":
            pass 
        elif self.agent_broker_type == "Custom":
            from agent_broker.custom_agent_broker import CustomAgentBroker
            self.agent_broker = CustomAgentBroker()
        elif self.agent_broker_type == "grpc" or self.agent_broker_type == "Local":
            from agent_broker.grpc_agent_broker import GrpcAgentBroker
            self.agent_broker = GrpcAgentBroker()
        else: #assume LFS
            from agent_broker.custom_agent_broker import CustomAgentBroker
            self.agent_broker = CustomAgentBroker()

    def get_agent_broker(self):
        #self.logger.info("[DataStoreFactory] Giving store with type '{0}' and id '{1}'".format(self.store_type, self.store))
        return self.agent_broker