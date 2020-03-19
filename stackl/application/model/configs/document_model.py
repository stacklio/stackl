from pydantic import BaseModel


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}
