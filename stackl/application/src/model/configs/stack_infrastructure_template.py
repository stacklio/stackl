from marshmallow import Schema, fields, post_load


class InfrastructureTarget:
    def __init__(self, environment="", location="", zone=""):
        self.environment = environment
        self.location = location
        self.zone = zone


class InfrastructureTargetSchema(Schema):
    environment = fields.String()
    location = fields.String()
    zone = fields.String()
    
    @post_load
    def make_infrastructure_target(self, data, **kwargs):
        return InfrastructureTarget(**data)


class StackInfrastructureTemplate:
    def __init__(self, name="", description="", category="configs", type="stack_infrastructure_template", infrastructure_targets=[], infrastructure_capabilities={}):
        self.name = name
        self.description = description
        self.type = type
        self.category = category
        self.infrastructure_targets = infrastructure_targets
        self.infrastructure_capabilities = infrastructure_capabilities


class StackInfrastructureTemplateSchema(Schema):
    name = fields.String()
    description = fields.String()
    type = fields.String()
    category = fields.String()
    infrastructure_targets = fields.List(fields.Nested(InfrastructureTargetSchema))
    infrastructure_capabilities = fields.Dict(keys=fields.Str(), values=fields.Dict(keys=fields.Str(), values=fields.Raw()))

    @post_load
    def make_stack_infrastructure_template(self, data, **kwargs):
        return StackInfrastructureTemplate(**data)
