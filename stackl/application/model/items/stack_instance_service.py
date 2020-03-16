from typing import Dict, Any, List

from pydantic import BaseModel

from model.items.functional_requirement_status import FunctionalRequirementStatus

class ConnectionCredentials(BaseModel):
    username: str = None
    password: str = None

class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    hosts: List[str] = None
    connection_credentials: ConnectionCredentials = None
    provisioning_parameters: Dict[str, Any] = None
    status: List[FunctionalRequirementStatus] = None
