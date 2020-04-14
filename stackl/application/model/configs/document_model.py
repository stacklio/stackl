from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint
from typing import Any


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}


class GetAllDocuments(BaseModel):
    name: str
    description = "GetAllDocuments"
    type: str
    documents: Any
