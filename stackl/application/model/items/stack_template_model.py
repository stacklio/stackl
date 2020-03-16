
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

from model.configs.infrastructure_target_model import InfrastructureTarget

##TODO model the set of potential solutions. HowTo model that sometimes some mix of suited targets won't work?
class StackTemplate(BaseModel):
    name: str
    type = "stack_template"
    services: Dict[str, Union(str, InfrastructureTarget)] = {}
    category = "items"
