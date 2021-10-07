"""
Module containing InfrastructureBaseDocument
"""
from typing import List

from pydantic import BaseModel

class PolicyDefinition(BaseModel):
    name: str
    service_kind: str
    parameters: dict = {}

class InfrastructureBaseDocument(BaseModel):
    """Class for Environment, Location and Zone"""
    name: str
    category: str
    description = "Base Document"
    type: str
    cloud_provider: str = ""
    params: dict = {}
    secrets: dict = {}
    outputs: dict = {}
    resources: dict = {}
    policies: List[PolicyDefinition]
    tags: dict = {}
    agent: str = ""
