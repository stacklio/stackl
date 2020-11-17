"""Module for Stackl Location"""
from core.models.configs.infrastructure_base_document import InfrastructureBaseDocument


class Location(InfrastructureBaseDocument):
    """Stackl Location document"""
    type = "location"
