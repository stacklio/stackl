"""
Module containing functional requirement classes
"""
from typing import Dict, Optional

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from .document_model import BaseDocument


class Invocation(BaseModel):
    """the invocation of a functional requirement"""
    description: str = ""
    tool: str
    image: str
    before_command: Optional[str] = ""
    playbook_path: str = ""
    ansible_role: str = ""
    serial: int = 10


class FunctionalRequirement(BaseDocument):
    """The functional Requirement Document"""
    type = "functional_requirement"
    invocation: Dict[str, Invocation]
    outputs: dict = {}
    outputs_format: str = "json"
    as_group: bool = False
