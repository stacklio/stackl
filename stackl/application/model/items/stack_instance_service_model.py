from typing import Dict, Any, List
from pydantic import BaseModel #pylint: disable=E0611 #error in pylint

from model.items.functional_requirement_status_model import FunctionalRequirementStatus

class ConnectionCredentials(BaseModel):
    username: str = None
    password: str = None

class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    hosts: List[str] = None
    provisioning_parameters: Dict[str, Any] = None
    provisioning_secrets: Dict[str, Any] = None
    status: List[FunctionalRequirementStatus] = None
