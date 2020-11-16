"""OPA broker factory module"""

from loguru import logger

from core.utils.stackl_singleton import Singleton
from .opa_broker import OPABroker


class OPABrokerFactory(metaclass=Singleton):  # pylint: disable=too-few-public-methods
    """Singleton class to keep state of the opa broker"""

    def __init__(self):
        logger.info("[OPABrokerFactory] Creating OPABroker")
        self.opa_broker = OPABroker()

    def get_opa_broker(self):
        """returns the opa broker"""
        return self.opa_broker
