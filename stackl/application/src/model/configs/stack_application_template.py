from marshmallow import Schema, fields, post_load


class StackApplicationTemplate:
    def __init__(self, name="", category="configs", description="", type="stack_application_template",
                 services=None, extra_functional_requirements=None):
        self.category = category
        if services is None:
            services = []
        if extra_functional_requirements is None:
            extra_functional_requirements = {}
        self.name = name
        self.description = description
        self.type = type
        self.services = services
        self.extra_functional_requirements = extra_functional_requirements


class StackApplicationTemplateSchema(Schema):
    name = fields.String()
    description = fields.String()
    type = fields.String()
    services = fields.List(fields.String())
    extra_functional_requirements = fields.Dict(keys=fields.Str(),
                                                values=fields.Raw())

    @post_load
    def make_stack_application_template(self, data, **kwargs):
        return StackApplicationTemplate(**data)
