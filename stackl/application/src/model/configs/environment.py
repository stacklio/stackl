from marshmallow import Schema, fields, post_load


class Environment:
    def __init__(self, name="", category="configs", description="", type="environment", params={}):
        self.name = name
        self.category = category
        self.description = description
        self.type = type
        self.params = params


class EnvironmentSchema(Schema):
    name = fields.String()
    category = fields.String()
    description = fields.String()
    type = fields.String()
    params = fields.Dict(keys=fields.String(), values=fields.Raw())

    @post_load
    def make_environment(self, data, **kwargs):
        return Environment(**data)
