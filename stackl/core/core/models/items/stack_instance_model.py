from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylin

from .stack_instance_service_model import StackInstanceService
from .stack_instance_status_model import StackInstanceStatus


class HostTarget(BaseModel):
    host: str
    target: str


class StackInstance(BaseModel):
    name: str
    type = "stack_instance"
    deleted: bool = False
    groups: Dict[str, List[HostTarget]] = {}
    instance_params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    instance_secrets: Dict[str, Any] = {}
    services: Dict[str, List[StackInstanceService]] = {}
    stack_infrastructure_template: str
    stack_application_template: str
    category = "items"
    status: List[StackInstanceStatus] = None
