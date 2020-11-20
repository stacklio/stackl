from typing import Any, Dict

from pydantic import BaseModel


class StackInstanceInvocation(BaseModel):
    """
    Possible options for creating a Stack Instance
    """
    params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    tags: Dict[str, str] = {}
    stack_infrastructure_template: str = "stackl"
    stack_application_template: str = "web"
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    replicas: Dict[str, int] = {}


class StackInstanceUpdate(BaseModel):
    """
    Options for updating a Stack Instance
    """
    params: Dict[str, Any] = {}
    service_params: Dict[str, Dict[str, Any]] = {}
    stack_instance_name: str = "default_test_instance"
    secrets: Dict[str, Any] = {}
    tags: Dict[str, str] = {}
    replicas: Dict[str, int] = {}
    disable_invocation: bool = False
