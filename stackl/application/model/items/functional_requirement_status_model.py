from enum import IntEnum

from pydantic import BaseModel

#TODO Bring this to the enum package
class Status(IntEnum):
    in_progress = 1
    ready = 2
    failed = 3

class FunctionalRequirementStatus(BaseModel):
    functional_requirement: str
    status: Status
    error_message: str = None