from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    provisioning_parameters: Dict[str, Any] = None
    secrets: Dict[str, Any] = None
    agent: str = ""
