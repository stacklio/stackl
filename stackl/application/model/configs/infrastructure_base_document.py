from typing import List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class InfrastructureBaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}
    outputs: dict = {}
    resources: dict = {}
    packages: List[str] = []
    tags: dict = {}
