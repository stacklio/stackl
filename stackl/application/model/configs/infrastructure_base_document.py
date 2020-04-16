from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint
from typing import List


class InfrastructureBaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}
    resources: dict = {}
    packages: List[str] = []
    tags: dict = {}