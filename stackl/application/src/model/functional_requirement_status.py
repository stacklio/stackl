from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum

class Status(Enum):
    in_progress = 1
    ready = 2
    failed = 3

class FunctionalRequirementStatus:
    def __init__(self, functional_requirement="", status=Status.in_progress, error_message=""):
        self.functional_requirement = functional_requirement
        self.status = status
        self.error_message = error_message

class FunctionalRequirementStatusSchema(Schema):
    functional_requirement = fields.String()
    status = EnumField(Status)
    error_message = fields.String()
