from typing import Dict, Any

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylin

from model.items.stack_instance_service_model import StackInstanceService


class StackInstance(BaseModel):
    name: str
    type = "stack_instance"
    deleted: bool = False
    instance_params: Dict[str, Any] = {}
    instance_secrets: Dict[str, Any] = {}
    services: Dict[str, StackInstanceService] = {}
    stack_infrastructure_template: str
    stack_application_template: str
    category = "items"
