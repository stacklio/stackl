from pydantic import BaseModel #pylint: disable=E0611 #error in pylint
from model.configs.document_model import BaseDocument


class Invocation(BaseModel):
    image: str
    description: str
    tool: str


class FunctionalRequirement(BaseDocument):
    type = "functional_requirement"
    invocation: Invocation
