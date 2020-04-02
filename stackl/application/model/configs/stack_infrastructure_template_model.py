from typing import List, Dict, Any
from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint

from model.configs.infrastructure_target_model import InfrastructureTarget


class StackInfrastructureTemplate(BaseModel):
    name: str
    description: str = ""
    type = "stack_infrastructure_template"
    category = "configs"
    infrastructure_targets: List[InfrastructureTarget]
    infrastructure_capabilities: Dict[str, Dict[str, Any]] = {}
