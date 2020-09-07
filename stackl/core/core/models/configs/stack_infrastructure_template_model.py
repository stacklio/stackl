from typing import List, Dict, Any

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from .infrastructure_target_model import InfrastructureTarget
from ..items.stack_infrastructure_target_model import StackInfrastructureTarget


class StackInfrastructureTemplate(BaseModel):
    name: str
    description: str = ""
    type = "stack_infrastructure_template"
    category = "configs"
    infrastructure_targets: List[InfrastructureTarget]
    infrastructure_capabilities: Dict[str, StackInfrastructureTarget] = {}
