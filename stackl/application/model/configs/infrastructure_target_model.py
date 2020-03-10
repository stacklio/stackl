from typing import List, Dict, Any

from pydantic import BaseModel


class InfrastructureTarget(BaseModel):
    environment: str
    location: str
    zone: str
