from enums.status_enum import Status
from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint


class FunctionalRequirementStatus(BaseModel):
    functional_requirement: str
    status: Status
    error_message: str = None
