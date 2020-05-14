from typing import Dict, Any

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylin

class Snapshot(BaseModel):
    name: str
    type = "snapshot"
    category = "history"
    snapshot: BaseModel