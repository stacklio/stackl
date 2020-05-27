from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from enums.status_enum import Status


class StackInstanceStatus(BaseModel):
    functional_requirement: str = ""
    infrastructure_target: str = ""
    service: str = ""
    status: Status = None
    error_message: str = None
