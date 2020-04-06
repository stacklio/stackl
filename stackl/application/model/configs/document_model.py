from typing import List, Dict

from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}
