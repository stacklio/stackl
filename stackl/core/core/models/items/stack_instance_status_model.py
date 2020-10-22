"""
Stack instance status model
"""
from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class StackInstanceStatus(BaseModel):
    """
    Stack instance status model
    """
    functional_requirement: str = ""
    infrastructure_target: str = ""
    service: str = ""
    status: str = ""
    error_message: str = None
