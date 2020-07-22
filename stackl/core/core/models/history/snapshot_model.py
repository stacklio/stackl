from typing import Any, Optional

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylin


class Snapshot(BaseModel):
    name: str
    type = "snapshot"
    category = "history"
    description: Optional[
        str] = "This is a snapshot of a document as given in the K/V snapshot"
    snapshot: Any
