from typing import List, Dict, Any

from model.configs.document_model import BaseDocument


class Service(BaseDocument):
    category = "items"
    type = "service"
    name: str
    functional_requirements: List[str]
    resource_requirements: Dict[str, Any] = None
