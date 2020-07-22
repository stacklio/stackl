from typing import Optional, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class PolicyTemplate(BaseModel):
    name: str
    description: Optional[str]
    category: str = "configs"
    type: str = "policy_template"
    policy: str
    inputs: List[str]
    outputs: List[str] = None

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "policy_example",
    #             "description": "example description",
    #             "policy": "",
    #             "inputs": ["string"],
    #             "category": "configs",
    #             "type": "policy_template"
    #         }
    #     }
