from enums.status_enum import Status
from pydantic import BaseModel

class FunctionalRequirementStatus(BaseModel):
    functional_requirement: str
    status: Status
    error_message: str = None
