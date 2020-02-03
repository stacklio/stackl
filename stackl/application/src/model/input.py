from marshmallow import Schema, fields


class InputAttributes:
    def __init__(self, required, type, default=None):
        self.required = required
        self.type = type
        self.default = default

class InputAttributesSchema(Schema):
    required = fields.Boolean()
    type = fields.String()
    default = fields.String()

class Input:
    def __init__(self, name, input_attributes):
        self.inputs = {}

class InputSchema(Schema):
    inputs = fields.Dict(keys=fields.Str(), values=fields.Nested(InputAttributesSchema))
