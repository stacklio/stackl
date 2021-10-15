"""
Stack Infrastructure Target model
"""
from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class StackInfrastructureTarget(BaseModel):
    """
    Stack Infrastructure Target model
    """
    provisioning_parameters: Dict[str, Any] = None
    cloud_provider: str = "generic"
    secrets: Dict[str, Any] = None
    resources: Dict[str, str] = None
    policies: List[Any] = None
    agent: str = ""
    tags: Dict[str, str] = None
