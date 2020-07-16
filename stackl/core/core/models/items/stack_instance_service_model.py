from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


class StackInstanceService(BaseModel):
    infrastructure_target: str = None
    provisioning_parameters: Dict[str, Any] = None
    cloud_provider: str = "generic"
    secrets: Dict[str, Any] = None
    resources: Dict[str, str] = None
    agent: str = ""
    packages: List[str] = None
    tags: Dict[str, str] = None
