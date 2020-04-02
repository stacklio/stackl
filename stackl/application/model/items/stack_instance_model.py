from typing import Dict
from pydantic import BaseModel  #pylint: disable=E0611 #error in pylin

from model.items.stack_instance_service_model import StackInstanceService


class StackInstance(BaseModel):
    name: str
    type = "stack_instance"
    deleted: bool = False
    services: Dict[str, StackInstanceService] = {}
    category = "items"
