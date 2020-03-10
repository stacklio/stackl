from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class Policy(BaseModel):
    name: str
    description: Optional[str]
    policy_in_rego: str