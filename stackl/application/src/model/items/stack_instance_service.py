from marshmallow import Schema, fields, post_load
from model.items.functional_requirement_status import FunctionalRequirementStatusSchema


class StackInstanceService:
    def __init__(self, infrastructure_target="", provisioning_parameters={}, status=[]):
        self.infrastructure_target = infrastructure_target
        self.provisioning_parameters = provisioning_parameters
        self.status = status


class StackInstanceServiceSchema(Schema):
    infrastructure_target = fields.String()
    provisioning_parameters = fields.Dict(keys=fields.String(), values=fields.String())
    status = fields.List(fields.Nested(FunctionalRequirementStatusSchema))

    @post_load
    def make_stack_instance_service(self, data, **kwargs):
        return StackInstanceService(**data)
