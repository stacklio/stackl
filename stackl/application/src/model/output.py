from marshmallow import Schema, fields

class OutputAttributes:
    def __init__(self, type):
        self.type = type

class OutputAttributesSchema(Schema):
    type = fields.String()

class Output:
    def __init__(self, name, outputs_attributes):
        self.outputs = {}

class OutputSchema(Schema):
    outputs = fields.Dict(keys=fields.Str(), values=fields.Nested(OutputAttributesSchema))
    

