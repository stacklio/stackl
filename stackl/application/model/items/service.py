from typing import List, Dict, Any

from model.configs.document import BaseDocument


class Service(BaseDocument):
    category = "items"
    type = "service"
    functional_requirements: List[str]
    non_functional_requirements: Dict[str, Any] = None
