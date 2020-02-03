from marshmallow import Schema, fields
from input import InputSchema
from output import OutputSchema
from invocation import InvocationSchema

class FunctionalRequirement:
    def __init__(self, name, type, input, output, invocation):
        self.name = name
        self.type = type
        self.input = input
        self.output = output
        self.invocation = invocation


class FunctionalRequirementSchema(Schema):
    name = fields.String()
    type = fields.String()
    input = fields.Nested(InputSchema)
    output = fields.Nested(OutputSchema)
    invocation = fields.Nested(InvocationSchema)
