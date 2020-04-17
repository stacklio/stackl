from typing import Any

from pydantic import BaseModel


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
