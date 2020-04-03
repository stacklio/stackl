from typing import Dict, List

from model.configs.document_model import BaseDocument


class Zone(BaseDocument):
    type = "zone"
    tags: Dict[str, str] = {}
    configs: List[str] = []
