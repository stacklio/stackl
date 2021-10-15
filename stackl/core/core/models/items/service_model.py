"""
Service model
"""
from typing import List, Dict, Any

from core.models.configs.document_model import BaseDocument
from pydantic import BaseModel  # pylint: disable=E0611 #error in pylin


class ServicePolicyDescription(BaseModel):
    name: str
    inputs: Dict[str, str] = {}
class Service(BaseDocument):
    """
    Service model
    """
    category = "items"
    type = "service"
    name: str
    kinds: List[str] = []
    functional_requirements: List[str]
    resource_requirements: Dict[str, Any] = {}
    service_policies: List[ServicePolicyDescription] = []

