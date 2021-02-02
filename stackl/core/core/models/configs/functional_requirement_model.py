"""
Module containing functional requirement classes
"""
from typing import Dict

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from .document_model import BaseDocument


class Invocation(BaseModel):
    """the invocation of a functional requirement"""
    description: str = None
    tool: str
    image: str
    before_command: str = None
    playbook_path: str = None
    serial: int = None


class FunctionalRequirement(BaseDocument):
    """The functional Requirement Document"""
    type = "functional_requirement"
    invocation: Dict[str, Invocation]
    outputs: dict = {}
    outputs_format: str = "json"
    as_group: bool = False
