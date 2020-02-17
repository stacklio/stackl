from typing import Dict, Any, List

from pydantic import BaseModel

from model.items.functional_requirement_status import FunctionalRequirementStatus


class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    provisioning_parameters: Dict[str, Any] = None
    status: List[FunctionalRequirementStatus] = None
