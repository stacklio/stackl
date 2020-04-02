from typing import List, Dict, Any
from pydantic import BaseModel #pylint: disable=E0611 #error in pylint

class StackApplicationTemplate(BaseModel):
    category = "configs"
    name: str
    description: str = ""
    type = "stack_application_template"
    services: List[str]
    policies: Dict[str, Any] = None
