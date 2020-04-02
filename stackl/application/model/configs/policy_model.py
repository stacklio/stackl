from typing import Optional
from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint


class Policy(BaseModel):
    id: str
    description: Optional[str]
    policy: str
