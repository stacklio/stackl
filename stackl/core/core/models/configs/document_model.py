"""
Base document model module
"""

from pydantic import BaseModel


class BaseDocument(BaseModel):
    """BaseDocument used by stackl documents"""
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
    secrets: dict = {}
