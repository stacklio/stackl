import logging

from opa_broker.opa_broker import OPABroker
from utils.stackl_singleton import Singleton

logger = logging.getLogger(__name__)


class OPABrokerFactory(metaclass=Singleton):
    def __init__(self):
        logger.info("[OPABrokerFactory] Creating OPABroker")
        self.opa_broker = OPABroker()

    def get_opa_broker(self):
        return self.opa_broker
