"""
Infrastructure Template model
"""
from typing import List, Dict

from pydantic import BaseModel

from .infrastructure_target_model import InfrastructureTarget
from ..items.stack_infrastructure_target_model import StackInfrastructureTarget


class StackInfrastructureTemplate(BaseModel):
    """
    Infrastructure Template model
    """
    name: str
    description: str = ""
    type = "stack_infrastructure_template"
    category = "configs"
    infrastructure_targets: List[InfrastructureTarget]
    infrastructure_capabilities: Dict[str, StackInfrastructureTarget] = {}
