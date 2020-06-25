from typing import Any

from pydantic import validator

from .task import Task


class StackTask(Task):
    topic: str = "stack_task"
    json_data: Any = None

    @validator('subtype')
    def valid_subtypes(cls, subtype):
        subtypes = [
            "GET_STACK",
            "GET_ALL_STACKS",
            "CREATE_STACK",
            "UPDATE_STACK",
            "DELETE_STACK",
        ]
        if subtype not in subtypes:
            raise ValueError("subtype for DocumentTask not valid")
        return subtype
