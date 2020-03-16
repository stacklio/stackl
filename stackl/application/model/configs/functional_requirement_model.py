from pydantic import BaseModel

from model.configs.document_model import BaseDocument


class Invocation(BaseModel):
    image: str
    description: str
    tool: str


class FunctionalRequirement(BaseDocument):
    type = "functional_requirement"
    invocation: Invocation
