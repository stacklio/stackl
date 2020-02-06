from marshmallow import Schema, fields, post_load
from model.items.stack_instance_service import StackInstanceServiceSchema


class StackInstance:
    def __init__(self, name, services={}, deleted=False, category="items", type="stack_instance"):
        self.name = name
        self.type = type
        self.deleted = deleted
        self.services = services
        self.category = category


class StackInstanceSchema(Schema):
    name = fields.String()
    type = fields.String()
    deleted = fields.Boolean()
    services = fields.Dict(keys=fields.String(), values=fields.Nested(StackInstanceServiceSchema))
    category = fields.String()

    @post_load
    def make_stack_instance(self, data, **kwargs):
        return StackInstance(**data)
