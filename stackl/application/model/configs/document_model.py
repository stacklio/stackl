from typing import List

from pydantic import BaseModel


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}
    configs: List[str] = []
