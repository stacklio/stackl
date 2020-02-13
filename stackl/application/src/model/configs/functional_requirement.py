from marshmallow import Schema, fields, post_load


class Invocation:
    def __init__(self, image="", description="", tool=""):
        self.image = image
        self.description = description
        self.tool = tool


class InvocationSchema(Schema):
    image = fields.String()
    description = fields.String()
    tool = fields.String()

    @post_load
    def make_invocation(self, data, **kwargs):
        return Invocation(**data)


class FunctionalRequirement:
    def __init__(self, name="", description="", type="functional_requirement", category="configs", invocation={},
                 params={}):
        self.name = name
        self.description = description
        self.type = type
        self.category = category
        self.invocation = invocation
        self.params = params


class FunctionalRequirementSchema(Schema):
    name = fields.String()
    description = fields.String()
    type = fields.String()
    category = fields.String()
    invocation = fields.Nested(InvocationSchema)
    params = fields.Dict(keys=fields.String(), values=fields.Raw())

    @post_load
    def make_functional_requirement(self, data, **kwargs):
        return FunctionalRequirement(**data)
