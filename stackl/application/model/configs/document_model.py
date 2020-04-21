from typing import Any, List

from pydantic import BaseModel


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}


class CollectionDocument(BaseModel):
    name: str
    description = "CollectionDocument"
    type: str
    documents: List[Any]
