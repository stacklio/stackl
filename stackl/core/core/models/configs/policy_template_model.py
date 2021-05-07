"""
PolicyTemplate model
"""
from typing import Optional, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class PolicyTemplate(BaseModel):
    """
    PolicyTemplate model
    """
    name: str
    description: Optional[str]
    category: str = "configs"
    type: str = "policy_template"
    inputs: List[str]
    outputs: List[str] = None
    policy: str = ""
