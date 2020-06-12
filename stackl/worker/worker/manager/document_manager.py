import json
import logging

from stackl.enums.cast_type import CastType
from stackl.enums.stackl_codes import StatusCode
from .manager import Manager
from stackl.models.configs.document_model import BaseDocument
from stackl.models.configs.environment_model import Environment
from stackl.models.configs.functional_requirement_model import FunctionalRequirement
from stackl.models.configs.location_model import Location
from stackl.models.configs.policy_template_model import PolicyTemplate
from stackl.models.configs.stack_application_template_model import StackApplicationTemplate
from stackl.models.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from stackl.models.configs.zone_model import Zone
from stackl.models.items.service_model import Service
from stackl.models.items.stack_instance_model import StackInstance
from stackl.stackl_globals import types, types_configs, types_items, types_history
from stackl.tasks.result_task import ResultTask
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.utils.stackl_exceptions import InvalidDocTypeError, InvalidDocNameError
from stackl.message_channel.message_channel_factory import MessageChannelFactory

logger = logging.getLogger("STACKL_LOGGER")


class DocumentManager(Manager):
    def __init__(self):
        super(DocumentManager, self).__init__()

        task_broker_factory = TaskBrokerFactory()
        self.task_broker = task_broker_factory.get_task_broker()
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

        self.snapshot_manager = None  #Given after initalisation by manager_factory

    def handle_task(self, task):
        logger.debug(f"[DocumentManager] handling document_task '{task}'")
        if task["subtype"] == "GET_DOCUMENT":
            (type_name, name) = task["args"]
            return_result = self.get_document(type=type_name, name=name)
        elif task["subtype"] == "COLLECT_DOCUMENT":
            type_name = task["args"]
            return_result = self.collect_documents(type_name=type_name)
        elif task["subtype"] == "POST_DOCUMENT":
            document = task["document"]
            return_result = self.write_document(document)
        elif task["subtype"] == "PUT_DOCUMENT":
            document = task["document"]
            return_result = self.write_document(document, overwrite=True)
        elif task["subtype"] == "DELETE_DOCUMENT":
            (type_name, name) = task["args"]
            return_result = self.delete_document(type=type_name, name=name)
        logger.debug(
            f"[DocumentManager] Handled document task. Creating ResultTask.")
        resultTask = ResultTask({
            'channel': task['return_channel'],
            'result_msg':
            f"DocumentTask with type '{task['subtype']}' was handled",
            'return_result': return_result,
            'result_code': StatusCode.OK,
            'cast_type': CastType.BROADCAST.value,
            'source_task': task
        })
        self.message_channel.publish(resultTask)

    # Rudimentary rollback system. It should also take into account the reason for the failure.
    # For instance, rollback create should behave differently if the failure was because the item already existed then when the problem occured during actual creation
    def rollback_task(self, task):
        logger.debug(f"[DocumentManager] rolling back document_task '{task}'")
        if task["subtype"] == "GET_DOCUMENT":
            logger.debug(
                f"[DocumentManager] rollback_task GET_DOCUMENT. Safe Task. Nothing to do."
            )
        elif task["subtype"] == "COLLECT_DOCUMENT":
            logger.debug(
                f"[DocumentManager] rollback_task COLLECT_DOCUMENT. Safe Task. Nothing to do."
            )
        elif task["subtype"] == "POST_DOCUMENT":
            document = task["document"]
            result = self.delete_document(type=document["type"],
                                          name=document["name"])
            logger.debug(
                f"[DocumentManager] rollback_task POST_DOCUMENT. Remove document if it did not yet exist and was created. Result '{result}'"
            )
        elif task["subtype"] == "PUT_DOCUMENT":
            document = task["document"]
            result = self.snapshot_manager.restore_snapshot(
                document["type"], document["name"])
            logger.debug(
                f"[DocumentManager] rollback_task PUT_DOCUMENT. Restored latest snapshot if it was present. Result '{result}'"
            )
        elif task["subtype"] == "DELETE_DOCUMENT":
            (type_name, name) = task["args"]
            result = self.snapshot_manager.restore_snapshot(type_name, name)
            logger.debug(
                f"[DocumentManager] rollback_task DELETE_DOCUMENT. Restored latest snapshot if it was present. Result '{result}'"
            )
        return result

    def get_document(self, **keys):
        logger.debug(f"[DocumentManager] get_document. Keys '{keys}'")
        keys = self._process_document_keys(keys)
        logger.debug(
            f"[DocumentManager] get_document. Processed keys '{keys}'")
        store_response = self.store.get(**keys)
        if store_response.status_code == StatusCode.NOT_FOUND:
            return {}
        return store_response.content

    def collect_documents(self, type_name):
        logger.debug(
            f"[DocumentManager] collect_documents. Collect all documents of type '{type_name}'"
        )
        if type_name in types_configs:
            category = "configs"
        elif type_name in types_items:
            category = "items"
        elif type_name in types_history or type_name.startswith("snapshot_"):
            category = "history"
        store_response = self.store.get_all(category, type_name)
        if store_response.status_code == StatusCode.NOT_FOUND:
            return {}
        return store_response.content

    def write_document(self, document, overwrite=False, make_snapshot=True):
        logger.debug(
            f"[DocumentManager] write_document.  Document: '{document}'")
        keys = self._process_document_keys(document)

        document['category'] = keys.get("category")
        document['type'] = keys.get("type")
        document['name'] = keys.get("name")
        document['description'] = keys.get("description")

        logger.debug("[DocumentManager] Checking if document already exists ")
        store_response = self.store.get(**keys)
        prev_document = store_response.content

        if store_response.status_code == StatusCode.NOT_FOUND:
            logger.debug(
                f"[DocumentManager] No document found yet. Creating document with data: {json.dumps(document)}"
            )
            store_response = self.store.put(document)
            return store_response.status_code
        if overwrite:
            prev_document_string = json.dumps(prev_document)
            logger.debug(
                f"[DocumentManager] Updating document with original contents: {prev_document_string}"
            )
            doc_new_string = json.dumps(document)
            logger.debug(
                f"[DocumentManager] Updating document with modified contents: {doc_new_string}"
            )
            if sorted(prev_document_string) == sorted(
                    doc_new_string
            ):  #Sorted since the doc might've changed the ordering
                logger.debug(
                    f"[DocumentManager] Original document and new document are the same! NOT updating"
                )
                return StatusCode.OK
            else:
                #Since we are overwriting, take a snapshot first
                if make_snapshot:
                    self.snapshot_manager.create_snapshot(
                        document["type"], document["name"])
                store_response = self.store.put(document)
                return store_response.status_code
        else:
            logger.debug(
                f"[DocumentManager] Document already exists and overwrite is false. Returning."
            )
            return StatusCode.BAD_REQUEST

    def delete_document(self, **keys):
        logger.debug(f"[DocumentManager] delete_document. Keys '{keys}'")
        keys = self._process_document_keys(keys)

        logger.debug("[DocumentManager] Checking if document actually exists")
        doc_obj = self.get_document(**keys)
        if doc_obj == {}:
            logger.debug(
                "[DocumentManager] No document found or already deleted. Nothing to do."
            )
        else:
            doc_org_string = json.dumps(doc_obj)
            logger.debug(
                f"[DocumentManager] Removing document with concent '{doc_org_string}'"
            )
            keys['file'] = doc_obj
            store_response = self.store.delete(**keys)
            logger.debug(
                f"[DocumentManager] status: {store_response.status_code}. Reason: {store_response.reason}"
            )
            if store_response.status_code == 200:
                logger.debug("[DocumentManager] Document deleted.")
            else:
                logger.debug("[DocumentManager] Document was not deleted.")
        return store_response.status_code

    def write_base_document(self, base_document: BaseDocument):
        store_response = self.store.put(base_document.dict())
        return store_response.content

    def get_policy_template(self, policy_name):
        """gets a PolicyTemplate from the store"""
        store_response = self.store.get(type="policy_template",
                                        name=policy_name,
                                        category="configs")
        policy = PolicyTemplate.parse_obj(store_response.content)
        return policy

    def write_policy_template(self, policy):
        """writes a PolicyTemplate to the store
        """
        store_response = self.store.put(policy.dict())
        return store_response.status_code

    def get_stack_instance(self, stack_instance_name):
        """gets a StackInstance Object from the store"""
        store_response = self.store.get(type="stack_instance",
                                        name=stack_instance_name,
                                        category="items")
        stack_instance = StackInstance.parse_obj(store_response.content)
        return stack_instance

    def write_stack_instance(self, stack_instance):
        """writes a StackInstance object to the store
        """
        store_response = self.store.put(stack_instance.dict())
        return store_response.status_code

    def get_stack_infrastructure_template(self,
                                          stack_infrastructure_template_name):
        """gets a StackInfrastructureTemplate Object from the store"""
        store_response = self.store.get(
            type="stack_infrastructure_template",
            name=stack_infrastructure_template_name,
            category="configs")
        stack_infrastructure_template = StackInfrastructureTemplate.parse_obj(
            store_response.content)
        return stack_infrastructure_template

    def write_stack_infrastructure_template(
        self, stack_infrastructure_template: StackInfrastructureTemplate):
        """writes a StackInfrastructureTemplate object to the store
        """
        store_response = self.store.put(stack_infrastructure_template.dict())
        return store_response.content

    def get_stack_application_template(
            self, stack_application_template_name) -> StackApplicationTemplate:
        """gets a StackApplicationTemplate Object from the store"""
        store_response = self.store.get(type="stack_application_template",
                                        name=stack_application_template_name,
                                        category="configs")
        stack_application_template = StackApplicationTemplate.parse_obj(
            store_response.content)
        return stack_application_template

    def write_stack_application_template(
        self, stack_application_template: StackApplicationTemplate):
        """writes a StackApplicationTemplate object to the store
        """
        store_response = self.store.put(stack_application_template.dict())
        return store_response.content

    def get_environment(self, environment_name):
        """gets a Environment Object from the store"""
        store_response = self.store.get(type="environment",
                                        name=environment_name,
                                        category="configs")
        environment = Environment.parse_obj(store_response.content)
        return environment

    def get_location(self, location_name):
        """gets a Location Object from the store"""
        store_response = self.store.get(type="location",
                                        name=location_name,
                                        category="configs")
        location = Location.parse_obj(store_response.content)
        return location

    def get_zone(self, zone_name):
        """gets a Zone Object from the store"""
        store_response = self.store.get(type="zone",
                                        name=zone_name,
                                        category="configs")
        zone = Zone.parse_obj(store_response.content)
        return zone

    def get_service(self, service_name):
        """gets a Service Object from the store"""
        store_response = self.store.get(type="service",
                                        name=service_name,
                                        category="items")
        service = Service.parse_obj(store_response.content)
        return service

    def write_service(self, service: Service):
        """writes a Service object to the store
        """
        store_response = self.store.put(service.dict())
        return store_response.content

    def get_functional_requirement(self, functional_requirement_name):
        """gets a FunctionalRequirement Object from the store"""
        store_response = self.store.get(type="functional_requirement",
                                        name=functional_requirement_name,
                                        category="configs")
        fr = FunctionalRequirement.parse_obj(store_response.content)
        return fr

    def write_functional_requirement(self, fr: FunctionalRequirement):
        """writes a Service object to the store
        """
        store_response = self.store.put(fr.dict())
        return store_response.content

    # Method processes and checks document keys.
    # Supports fuzzy get - trying to determine keys from other keys
    def _process_document_keys(self, keys):
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
