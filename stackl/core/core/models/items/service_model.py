"""
Service model
"""
from typing import List, Dict, Any

from core.models.configs.document_model import BaseDocument


class Service(BaseDocument):
    """
    Service model
    """
    category = "items"
    type = "service"
    name: str
    functional_requirements: List[str]
    resource_requirements: Dict[str, Any] = None
    service_policies: List[Any] = None
