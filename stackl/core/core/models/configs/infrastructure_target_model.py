from pydantic import BaseModel  #pylint: disable=E0611 #error in pylint


class InfrastructureTarget(BaseModel):
    environment: str
    location: str
    zone: str
