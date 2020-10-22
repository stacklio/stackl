"""
Infrastructure target model
"""
from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint


class InfrastructureTarget(BaseModel):
    """
    Infrastructure target model
    """
    environment: str
    location: str
    zone: str
