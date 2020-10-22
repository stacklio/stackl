"""
Environment model
"""
from .infrastructure_base_document import InfrastructureBaseDocument


class Environment(InfrastructureBaseDocument):
    """
    Environment model
    """
    type = "environment"
    cloud_provider: str = "generic"
