from typing import Dict

from pydantic import BaseModel

from model.items.stack_instance_service import StackInstanceService


class StackInstance(BaseModel):
    name: str
    type = "stack_instance"
    deleted: bool = False
    services: Dict[str, StackInstanceService] = {}
    category = "items"
