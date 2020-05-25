from typing import Any, List

from pydantic import BaseModel


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}  #TODO This should not be a part of a base document but atm the system relies on it
    secrets: dict = {} #TODO This should not be a part of a base document but atm the system relies on it
    class Config:
        schema_extra = {
            "example": {
                "name": "stack_instance_document_example",
                "description":
                "an example of a document, using the stack_instance type",
                "stack_infrastructure_template": "Not applicable",
                "stack_application_template": "Not applicable",
                "category": "items",
                "type": "stack_instance"
            }
        }


class ResultDocument(BaseModel):
    name: str
    description = "ResultDocument"
    type: str
    result_code: int


class CollectionDocument(BaseModel):
    name: str
    description = "CollectionDocument"
    type: str
    documents: List[Any]
