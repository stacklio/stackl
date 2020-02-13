from marshmallow import Schema, fields, post_load


class Zone:
    def __init__(self, name="", category="configs", description="", type="zone", params={}):
        self.category = category
        self.name = name
        self.description = description
        self.type = type
        self.params = params


class ZoneSchema(Schema):
    name = fields.String()
    description = fields.String()
    category = fields.String()
    type = fields.String()
    params = fields.Dict(keys=fields.String(), values=fields.Raw())

    @post_load
    def make_zone(self, data, **kwargs):
        return Zone(**data)
