from typing import Dict, List

from model.configs.document_model import BaseDocument


class Environment(BaseDocument):
    type = "environment"
    tags: Dict[str, str] = {}
    configs: List[str] = []