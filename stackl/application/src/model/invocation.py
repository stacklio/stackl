from marshmallow import Schema, fields

class Invocation:
    def __init__(self, handler, version, target, description):
        self.handler = handler
        self.version = version
        self.target = target
        self.description = description

class InvocationSchema(Schema):
    handler = fields.String()
    version = fields.String()
    target = fields.String()
    description = fields.String()