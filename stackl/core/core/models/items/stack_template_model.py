"""
Stack template model
"""
from typing import Dict, Any

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class StackTemplate(BaseModel):
    """
    Stack template model
    """
    name: str
    type = "stack_template"
    services: Dict[str, Any] = {}
    category = "items"
