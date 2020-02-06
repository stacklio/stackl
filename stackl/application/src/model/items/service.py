from marshmallow import Schema, fields, post_load


class Service:
    def __init__(self, name="", description="", type="service", functional_requirements=[], non_functional_requirements={}, params={}):
        self.name = name
        self.description = description
        self.type = type
        self.functional_requirements = functional_requirements
        self.params = params
        self.non_functional_requirements = non_functional_requirements


class ServiceSchema(Schema):
    name = fields.String()
    description = fields.String()
    type = fields.String()
    functional_requirements = fields.List(fields.String())
    non_functional_requirements = fields.Dict(keys=fields.String(), values=fields.Raw())
    params = fields.Dict(keys=fields.String(), values=fields.Raw())

    @post_load
    def make_service(self, data, **kwargs):
        return Service(**data)
