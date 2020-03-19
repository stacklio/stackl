from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class Policy(BaseModel):
    id: str
    description: Optional[str]
    policy: str