from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from enum import IntEnum


class Status(IntEnum):
    READY = 0
    FAILED = 1
    PROGRESS = 2


class StackInstanceStatus(BaseModel):
    functional_requirement: str = ""
    infrastructure_target: str = ""
    service: str = ""
    status: Status = Status.READY
    error_message: str = None
