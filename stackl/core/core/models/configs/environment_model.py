from .infrastructure_base_document import InfrastructureBaseDocument


class Environment(InfrastructureBaseDocument):
    type = "environment"
    cloud_provider: str = "generic"
