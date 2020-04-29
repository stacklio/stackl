from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from model.items.functional_requirement_status_model import FunctionalRequirementStatus


class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    provisioning_parameters: Dict[str, Any] = None
    secrets: Dict[str, Any] = None
    status: List[FunctionalRequirementStatus] = None
