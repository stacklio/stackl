from marshmallow import Schema, fields, post_load


class Location:
    def __init__(self, name="", category="configs", description="", type="location", params={}):
        self.name = name
        self.category = category
        self.description = description
        self.type = type
        self.params = params


class LocationSchema(Schema):
    name = fields.String()
    description = fields.String()
    type = fields.String()
    params = fields.Dict(keys=fields.String(), values=fields.Raw())

    @post_load
    def make_location(self, data, **kwargs):
        return Location(**data)
