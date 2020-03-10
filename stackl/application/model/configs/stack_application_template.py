from typing import List, Dict, Any

from pydantic import BaseModel


class StackApplicationTemplate(BaseModel):
    category = "configs"
    name: str
    description: str = ""
    type = "stack_application_template"
    services: List[str]
    policies: Dict[str, Any] = None
