from typing import Optional, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class PolicyTemplate(BaseModel):
    name: str
    description: Optional[str]
    category: str = "configs"
    type: str = "policy"
    policy: str
    inputs: List[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "policy_template_example",
                "description": "example descrition",
                "policy": "",
                "inputs": ["string"],
                "category": "configs",
                "type": "policy_template"
            }
        }
