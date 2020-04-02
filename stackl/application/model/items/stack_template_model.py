from typing import  Dict, Union
from pydantic import BaseModel #pylint: disable=E0611 #error in pylint

from model.configs.infrastructure_target_model import InfrastructureTarget

##TODO model the set of potential solutions. How to model that sometimes some mix of suited targets won't work?
class StackTemplate(BaseModel):
    name: str
    type = "stack_template"
    services: Dict[str, Union(str, InfrastructureTarget)] = {}
    category = "items"
