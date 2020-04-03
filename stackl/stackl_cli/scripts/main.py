from json_mapper import JsonMapper
import json
from glom import glom
with open('terraform.json') as r:
    json_document = json.load(r)
with open('terraform-output-spec.json') as r:
    json_spec = json.load(r)

# print(JsonMapper(json_document).map(json_spec))
result = {}
spec = {'guest_id': ("values.root_module.resources", [('values.guest_id')])}
print(glom(json_document, spec, default='nada'))
# for field_name, field_spec in json_spec.items():
#     result[field_name] = glom(json_document, field_spec)
# print(result)
