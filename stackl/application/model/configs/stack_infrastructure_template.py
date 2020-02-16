from typing import List, Dict, Any

from pydantic import BaseModel


class InfrastructureTarget(BaseModel):
    environment: str
    location: str
    zone: str


class StackInfrastructureTemplate(BaseModel):
    name: str
    description: str = ""
    type = "stack_infrastructure_template"
    category = "configs"
    infrastructure_targets: List[InfrastructureTarget]
    infrastructure_capabilities: Dict[str, Dict[str, Any]] = {}
