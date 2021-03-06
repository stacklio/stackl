"""Module for Stackl Documents"""

import json
from typing import List

from loguru import logger
from pydantic import parse_obj_as

from core.enums.stackl_codes import StatusCode
from core.models.configs.document_model import BaseDocument
from core.models.configs.environment_model import Environment
from core.models.configs.functional_requirement_model import FunctionalRequirement
from core.models.configs.location_model import Location
from core.models.configs.policy_template_model import PolicyTemplate
from core.models.configs.stack_application_template_model import StackApplicationTemplate
from core.models.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from core.models.configs.zone_model import Zone
from core.models.history.snapshot_model import Snapshot
from core.models.items.service_model import Service
from core.models.items.stack_instance_model import StackInstance
from core.utils.stackl_exceptions import InvalidDocTypeError, InvalidDocNameError
from .manager import Manager

types_categories = ["configs", "items", "history"]
types_configs = [
    "environment", "location", "zone", "stack_application_template",
    "stack_infrastructure_template", "functional_requirement",
    "resource_requirement", "authentication", "policy_template"
]
types_items = [
    "stack_instance", "stack_template", "infrastructure_target", "service"
]
types_history = ["snapshot", "log"]
types = types_configs + types_items + types_history


def _process_document_keys(keys):
    """
    Method processes and checks document keys.
    Supports fuzzy get - trying to determine keys from other keys
    """
    # process to lowercase
    keys = {
        k.lower() if isinstance(k, str) else k:
            v.lower() if isinstance(v, str) else v
        for k, v in keys.items()
    }

    if not keys.get("category", None):
        type_name = keys.get("type", "none")
        if type_name in types_configs:
            keys["category"] = "configs"
        elif type_name in types_items:
            keys["category"] = "items"
        elif type_name in types_history:
            keys["category"] = "history"
        else:
            raise InvalidDocTypeError(type_name)
    if not keys.get("type", None):
        name = keys.get("name", "none")
        derived_type_from_name_list = [
            poss_type for poss_type in types if poss_type in name
        ]
        if len(derived_type_from_name_list) == 1:
            keys["type"] = derived_type_from_name_list[0]
        else:
            raise InvalidDocNameError(name)
    logger.debug(
        f"[DocumentManager] _process_document_keys. After _process_document_keys '{keys}'"
    )
    return keys


class DocumentManager(Manager):
    """Manager for everything document related"""

    def get_document(self, **keys):
        """Get a document from the chosen store"""
        logger.debug(f"[DocumentManager] get_document. Keys '{keys}'")
        keys = _process_document_keys(keys)
        logger.debug(
            f"[DocumentManager] get_document. Processed keys '{keys}'")
        store_response = self.store.get(**keys)
        if store_response.status_code == StatusCode.NOT_FOUND:
            return {}
        return store_response.content

    def write_document(self, document, overwrite=False):
        """Writes a document to the store"""
        logger.debug(
            f"[DocumentManager] write_document.  Document: '{document}'")
        keys = _process_document_keys(document)

        document['category'] = keys.get("category")
        document['type'] = keys.get("type")
        document['name'] = keys.get("name")
        document['description'] = keys.get("description")

        logger.debug("[DocumentManager] Checking if document already exists ")
        store_response = self.store.get(**keys)
        prev_document = store_response.content

        if store_response.status_code == StatusCode.NOT_FOUND:
            logger.debug(
                f" No document found yet. Creating document with data: {json.dumps(document)}"
            )
            store_response = self.store.put(document)
            return store_response.status_code
        if overwrite:
            prev_document_string = json.dumps(prev_document)
            logger.debug(
                f"Updating document with original contents: {prev_document_string}"
            )
            doc_new_string = json.dumps(document)
            logger.debug(
                f"Updating document with modified contents: {doc_new_string}"
            )
            if sorted(prev_document_string) == sorted(
                    doc_new_string
            ):  # Sorted since the doc might've changed the ordering
                logger.debug(
                    "Original document and new document are the same! NOT updating"
                )
                return StatusCode.OK

            store_response = self.store.put(document)
            return store_response.status_code
        logger.debug(
            "Document already exists and overwrite is false. Returning."
        )
        return StatusCode.BAD_REQUEST

    def write_base_document(self, base_document: BaseDocument):
        """Writes a base document to the store"""
        store_response = self.store.put(base_document.dict())
        return store_response.content

    def delete_base_document(self, document_type, name):
        """Deletes a base document"""
        store_response = self.store.delete(type=document_type,
                                           category="configs",
                                           name=name)
        return store_response

    def get_policy_template(self, policy_name):
        """gets a PolicyTemplate from the store"""
        store_response = self.store.get(type="policy_template",
                                        name=policy_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        policy = PolicyTemplate.parse_obj(store_response.content)
        return policy

    def get_policy_templates(self):
        """gets all PolicyTemplate from the store"""
        store_response = self.store.get_all(document_type="policy_template",
                                            category="configs")
        policy_templates = parse_obj_as(List[PolicyTemplate],
                                        store_response.content)
        return policy_templates

    def write_policy_template(self, policy):
        """writes a PolicyTemplate to the store
        """
        store_response = self.store.put(policy.dict())
        policy = PolicyTemplate.parse_obj(store_response.content)
        return policy

    def delete_policy_template(self, name):
        """Deletes a PolicyTemplate from the store"""
        store_response = self.store.delete(type="policy_template",
                                           category="configs",
                                           name=name)
        return store_response

    def get_stack_instance(self, stack_instance_name):
        """gets a StackInstance Object from the store"""
        store_response = self.store.get(type="stack_instance",
                                        name=stack_instance_name,
                                        category="items")
        if store_response.status_code == 404:
            logger.debug("not found returning none")
            return None
        stack_instance = StackInstance.parse_obj(store_response.content)
        return stack_instance

    def get_stack_instances(self):
        """Get all stack instances"""
        store_response = self.store.get_all(document_type="stack_instance",
                                            category="items")
        stack_instances = parse_obj_as(List[StackInstance],
                                       store_response.content)
        if store_response.status_code == 404:
            return None
        return stack_instances

    def write_stack_instance(self, stack_instance):
        """writes a StackInstance object to the store
        """
        store_response = self.store.put(stack_instance.dict())
        return store_response.status_code

    def delete_stack_instance(self, name):
        """Delete a stack instance by name"""
        store_response = self.store.delete(type="stack_instance",
                                           name=name,
                                           category="items")
        return store_response

    def get_stack_infrastructure_template(self,
                                          stack_infrastructure_template_name):
        """gets a StackInfrastructureTemplate Object from the store"""
        store_response = self.store.get(
            type="stack_infrastructure_template",
            name=stack_infrastructure_template_name,
            category="configs")
        if store_response.status_code == 404:
            return None
        stack_infrastructure_template = StackInfrastructureTemplate.parse_obj(
            store_response.content)
        return stack_infrastructure_template

    def get_stack_infrastructure_templates(self):
        """Get a stack infrastructure template"""
        store_response = self.store.get_all(
            document_type="stack_infrastructure_template", category="configs")
        sits = parse_obj_as(List[StackInfrastructureTemplate],
                            store_response.content)
        return sits

    def write_stack_infrastructure_template(
            self, stack_infrastructure_template: StackInfrastructureTemplate):
        """writes a StackInfrastructureTemplate object to the store
        """
        store_response = self.store.put(stack_infrastructure_template.dict())
        return store_response.content

    def delete_stack_infrastructure_template(self, name):
        """Deletes a SIT from the store"""
        store_response = self.store.delete(
            type="stack_infrastructure_template",
            category="configs",
            name=name)
        return store_response

    def get_stack_application_template(
            self, stack_application_template_name) -> StackApplicationTemplate:
        """Gets a StackApplicationTemplate Object from the store"""
        store_response = self.store.get(type="stack_application_template",
                                        name=stack_application_template_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        stack_application_template = StackApplicationTemplate.parse_obj(
            store_response.content)
        return stack_application_template

    def get_stack_application_templates(
            self) -> List[StackApplicationTemplate]:
        """Gets a Stack Application Template from the store"""
        store_response = self.store.get_all(document_type="stack_application_template",
                                            category="configs")
        sats = parse_obj_as(List[StackApplicationTemplate],
                            store_response.content)
        return sats

    def write_stack_application_template(
            self, stack_application_template: StackApplicationTemplate):
        """writes a StackApplicationTemplate object to the store
        """
        store_response = self.store.put(stack_application_template.dict())
        return store_response.content

    def delete_stack_application_template(self, name):
        """Deletes a stack application Template"""
        store_response = self.store.delete(type="stack_application_template",
                                           category="configs",
                                           name=name)
        return store_response

    def get_environment(self, environment_name):
        """gets a Environment Object from the store"""
        store_response = self.store.get(type="environment",
                                        name=environment_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        environment = Environment.parse_obj(store_response.content)
        return environment

    def get_environments(self):
        """Get all environments from the store"""
        store_response = self.store.get_all(document_type="environment",
                                            category="configs")
        environments = parse_obj_as(List[Environment], store_response.content)
        return environments

    def get_location(self, location_name):
        """gets a Location Object from the store"""
        store_response = self.store.get(type="location",
                                        name=location_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        location = Location.parse_obj(store_response.content)
        return location

    def get_locations(self):
        """Gets all locations from the store"""
        store_response = self.store.get_all(document_type="location",
                                            category="configs")
        locations = parse_obj_as(List[Location], store_response.content)
        return locations

    def get_zone(self, zone_name):
        """gets a Zone Object from the store"""
        store_response = self.store.get(type="zone",
                                        name=zone_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        zone = Zone.parse_obj(store_response.content)
        return zone

    def get_zones(self):
        """Gets all zones from the store"""
        store_response = self.store.get_all(document_type="zone", category="configs")
        zone = parse_obj_as(List[Zone], store_response.content)
        return zone

    def get_service(self, service_name):
        """gets a Service Object from the store"""
        store_response = self.store.get(type="service",
                                        name=service_name,
                                        category="items")
        if store_response.status_code == 404:
            return None

        service = Service.parse_obj(store_response.content)
        return service

    def get_services(self):
        """Gets all the services from the store"""
        store_response = self.store.get_all(document_type="service", category="items")
        services = parse_obj_as(List[Service], store_response.content)
        return services

    def write_service(self, service: Service):
        """writes a Service object to the store
        """
        store_response = self.store.put(service.dict())
        return store_response.content

    def delete_service(self, name):
        """Deletes a service from the store"""
        self.store.delete(type="service", name=name, category="items")

    def get_functional_requirement(self, functional_requirement_name):
        """gets a FunctionalRequirement Object from the store"""
        store_response = self.store.get(type="functional_requirement",
                                        name=functional_requirement_name,
                                        category="configs")
        if store_response.status_code == 404:
            return None

        fr = FunctionalRequirement.parse_obj(store_response.content)
        return fr

    def get_functional_requirements(self) -> List[FunctionalRequirement]:
        """gets a FunctionalRequirement Object from the store"""
        store_response = self.store.get_all(document_type="functional_requirement",
                                            category="configs")
        fr = parse_obj_as(List[FunctionalRequirement], store_response.content)
        return fr

    def write_functional_requirement(self, functional_requirement: FunctionalRequirement):
        """writes a Service object to the store
        """
        store_response = self.store.put(functional_requirement.dict())
        return store_response.content

    def delete_functional_requirement(self, name: str):
        """Deletes a functional requirement from the store"""
        self.store.delete(type="functional_requirement",
                          name=name,
                          category="configs")

    def get_snapshot(self, name) -> Snapshot:
        """Get a snapshot from the store"""
        store_response = self.store.get(category="history",
                                        type="snapshot",
                                        name=name)
        if store_response.status_code == 404:
            return None

        snapshot = Snapshot.parse_obj(store_response.content)
        return snapshot

    def get_snapshots(self, document_type, name):
        """Gets all snapshots from the store of a document"""
        store_response = self.store.get_all(document_type=document_type,
                                            category="history",
                                            wildcard_prefix=f"{name}")

        return store_response.content

    def delete_snapshot(self, name: str):
        """Delete a snapshot from the store"""
        self.store.delete(type="snapshot", name=name, category="history")
