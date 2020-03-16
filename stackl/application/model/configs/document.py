from pydantic import BaseModel


class BaseDocument(BaseModel):
    name: str
    category: str
    description = "Base Document"
    type: str
    params: dict = {}

#TODO remove and replace with separate policy_model.py
class PolicyDocument(BaseDocument):
    id: str
    policy: dict = {}
