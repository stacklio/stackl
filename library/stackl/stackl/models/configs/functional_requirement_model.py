from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint

from .document_model import BaseDocument


class Invocation(BaseModel):
    image: str
    description: str
    tool: str
    as_group: bool = False


class FunctionalRequirement(BaseDocument):
    type = "functional_requirement"
    invocation: Invocation
    outputs: dict = {}
