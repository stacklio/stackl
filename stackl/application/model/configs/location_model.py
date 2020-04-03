from typing import Dict, List

from model.configs.document_model import BaseDocument


class Location(BaseDocument):
    type = "location"
    tags: Dict[str, str] = {}
    configs: List[str] = []