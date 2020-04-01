import logging

from utils.general_utils import get_config_key
from utils.stackl_singleton import Singleton

logger = logging.getLogger("STACKL_LOGGER")

class AgentBrokerFactory(metaclass=Singleton):

    def __init__(self):
        self.agent_broker_type = get_config_key('AGENT_BROKER')

        logger.info("[AgentBrokerFactory] Creating Agent Broker with type: %s", self.agent_broker_type)
        self.agent_broker = None

        if self.agent_broker_type == "gitlab-runner":
            pass
        elif self.agent_broker_type == "Custom":
            from agent_broker.custom_agent_broker import CustomAgentBroker
            self.agent_broker = CustomAgentBroker()
        elif self.agent_broker_type == "grpc" or self.agent_broker_type == "Local":
            from agent_broker.grpc_agent_broker import GrpcAgentBroker
            self.agent_broker = GrpcAgentBroker()
        else:
            from agent_broker.custom_agent_broker import CustomAgentBroker
            self.agent_broker = CustomAgentBroker()

    def get_agent_broker(self):
        return self.agent_broker
