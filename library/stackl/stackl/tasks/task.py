import logging
from abc import ABC
from typing import Any

from pydantic import BaseModel
from stackl.utils.general_utils import generate_random_string, get_hostname

from loguru import logger


class Task(BaseModel, ABC):
    source = None
    topic: str
    cast_type: str = "anycast"
    channel: str = None
    id: str = generate_random_string()
    source: Any = get_hostname()
    args: Any = None
    return_channel: str = None
    timeout: int = 5
    subtype: str = None
