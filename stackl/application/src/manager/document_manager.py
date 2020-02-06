from globals import types, types_configs, types_items
import json 

from logger import Logger
from manager import Manager
from model.configs.functional_requirement import FunctionalRequirementSchema
from model.configs.stack_application_template import StackApplicationTemplateSchema
from model.items.service import ServiceSchema
from task.result_task import ResultTask
from enums.stackl_codes import StatusCode
from enums.cast_type import CastType
from utils.stackl_exceptions import InvalidDocTypeError, InvalidDocNameError
from task_broker.task_broker_factory import TaskBrokerFactory
from model.items.stack_instance import StackInstanceSchema
from model.configs.stack_infrastructure_template import StackInfrastructureTemplateSchema
from model.configs.environment import EnvironmentSchema
from model.configs.location import LocationSchema
from model.configs.zone import ZoneSchema


class DocumentManager(Manager):

    def __init__(self, manager_factory):
        super(DocumentManager, self).__init__(manager_factory)
        self.logger = Logger("DocumentManager")
        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker =self.task_broker_factory.get_task_broker()

    def handle_task(self, document_task): 
        self.logger.log("[DocumentManager] handling subtasks of task_obj {0}".format(document_task))
        try:
            for subtask in document_task["subtasks"]:
                self.logger.log("[DocumentManager] handling subtask '{0}'".format(subtask))
                if subtask == "POST_DOCUMENT":
                    document = document_task["document"]
                    status_code = self.write_document(document_name = document['name'], type = document['type'], file = document['payload'], description = document['description'])
                elif subtask == "PUT_DOCUMENT":
                    document = document_task["document"]
                    status_code = self.write_document(document_name = document['name'], type = document['type'], file = document['payload'], description = document['description'])
                elif subtask == "DELETE_DOCUMENT":
                    document = document_task["document"]
                    status_code = self.remove_document(document_name = document['name'], type = document['type'])

                if status_code not in {StatusCode.OK, StatusCode.CREATED}:
                    raise Exception("[DocumentManager] Processing subtask failed. Status_code '{0}'".format(status_code))
            self.logger.log("[DocumentManager] Succesfully handled document task. Creating ResultTask.")
            self.task_broker.give_task(ResultTask({
                    'channel': document_task['return_channel'],
                    'result': "success",
                    'cast_type': CastType.BROADCAST.value,
                    'source_task': document_task
            })) #this way the STACKL broker is notified of the result and wheter he should remove the task from the task queue
        except Exception as e:
            self.logger.error("[DocumentManager] Error with processing task. Error: '{0}'".format(e))

    def get_document(self, **keys):
        self.logger.log("[DocumentManager] get_document. Keys '{0}'".format(keys))
        keys = self._process_document_keys(keys)
        self.logger.log("[DocumentManager] get_document. Post process Keys '{0}'".format(keys))
        try:
            store_response = self.store.get(**keys)
            if store_response.status_code == StatusCode.NOT_FOUND:
                return {}
            else: 
                return store_response.content 
        except Exception as e:
            self.logger.error("[DocumentManager] Exception occured in get_document: {0}. Returning empty object".format(str(e)))
            return None

    def get_stack_instance(self, stack_instance_name):
        """gets a StackInstance Object from the store"""
        store_response = self.store.get(type="stack_instance", document_name=stack_instance_name, category="items")
        schema = StackInstanceSchema()
        stack_instance = schema.load(store_response.content)
        return stack_instance
    
    def write_stack_instance(self, stack_instance):
        """writes a StackInstance object to the store
        """
        stack_instance_schema = StackInstanceSchema()
        store_response = self.store.put(stack_instance_schema.dump(stack_instance))
        return store_response.status_code

    def get_stack_infrastructure_template(self, stack_infrastructure_template_name):
        """gets a StackInfrastructureTemplate Object from the store"""
        store_response = self.store.get(type="stack_infrastructure_template", document_name=stack_infrastructure_template_name, category="configs")
        schema = StackInfrastructureTemplateSchema()
        stack_infrastructure_template = schema.load(store_response.content)
        return stack_infrastructure_template
    
    def write_stack_infrastructure_template(self, stack_infrastructure_template):
        """writes a StackInfrastructureTemplate object to the store
        """
        stack_infrastructure_template_schema = StackInfrastructureTemplateSchema()
        store_response = self.store.put(stack_infrastructure_template_schema.dump(stack_infrastructure_template))
        return store_response.status_code

    def get_stack_application_template(self, stack_application_template_name):
        """gets a StackApplicationTemplate Object from the store"""
        store_response = self.store.get(type="stack_application_template",
                                        document_name=stack_application_template_name, category="configs")
        schema = StackApplicationTemplateSchema()
        stack_application_template = schema.load(store_response.content)
        return stack_application_template

    def write_stack_application_template(self, stack_application_template):
        """writes a StackApplicationTemplate object to the store
        """
        stack_application_template_schema = StackApplicationTemplateSchema()
        store_response = self.store.put(stack_application_template_schema.dump(stack_application_template))
        return store_response.status_code

    def get_environment(self, environment_name):
        """gets a Environment Object from the store"""
        store_response = self.store.get(type="environment", document_name=environment_name, category="configs")
        schema = EnvironmentSchema()
        environment = schema.load(store_response.content)
        return environment
    
    def write_environment(self, environment):
        """writes a StackInstance object to the store
        """
        environment_schema = EnvironmentSchema()
        store_response = self.store.put(environment_schema.dump(environment))
        return store_response.status_code

    def get_location(self, location_name):
        """gets a Location Object from the store"""
        store_response = self.store.get(type="location", document_name=location_name, category="configs")
        schema = LocationSchema()
        location = schema.load(store_response.content)
        return location
    
    def write_location(self, location):
        """writes a Location object to the store
        """
        location_schema = LocationSchema()
        store_response = self.store.put(location_schema.dump(location))
        return store_response.status_code

    def get_zone(self, zone_name):
        """gets a Zone Object from the store"""
        store_response = self.store.get(type="zone", document_name=zone_name, category="configs")
        schema = ZoneSchema()
        zone = schema.load(store_response.content)
        return zone
    
    def write_zone(self, zone):
        """writes a Zone object to the store
        """
        zone_schema = ZoneSchema()
        store_response = self.store.put(zone_schema.dump(zone))
        return store_response.status_code

    def get_service(self, service_name):
        """gets a Service Object from the store"""
        store_response = self.store.get(type="service", document_name=service_name, category="items")
        schema = ServiceSchema()
        service = schema.load(store_response.content)
        return service

    def write_service(self, service):
        """writes a Service object to the store
        """
        service_schema = ServiceSchema()
        store_response = self.store.put(service_schema.dump(service))
        return store_response.status_code

    def get_functional_requirement(self, functional_requirement_name):
        """gets a FunctionalRequirement Object from the store"""
        store_response = self.store.get(type="functional_requirement", document_name=functional_requirement_name, category="configs")
        schema = FunctionalRequirementSchema()
        service = schema.load(store_response.content)
        return service

    def write_functional_requirement(self, functional_requirement):
        """writes a FunctionalRequirement object to the store
        """
        functional_requirement_schema = FunctionalRequirementSchema()
        store_response = self.store.put(functional_requirement_schema.dump(functional_requirement))
        return store_response.status_code

    def write_document(self, **keys):
        self.logger.log("[DocumentManager] write_document.  Keys '{0}'".format(keys))
        keys = self._process_document_keys(keys)
        
        document = keys.get("file")
        document['category'] = keys.get("category")
        document['type'] = keys.get("type")
        document['name'] = keys.get("document_name")
        document['description'] = keys.get("description")

        self.logger.log("[DocumentManager] Checking if document already exists ")
        store_response = self.store.get(**keys)
        prev_document = store_response.content


        if store_response.status_code == StatusCode.NOT_FOUND:
            self.logger.log("[DocumentManager] No document found yet. Creating document with data: " + str(json.dumps(document)))
            store_response = self.store.put(document)

            return store_response.status_code
        else:
            prev_document_string = json.dumps(prev_document)
            self.logger.log("[DocumentManager] Updating document with original contents: " + prev_document_string)
            doc_new_string = json.dumps(document)
            self.logger.log("[DocumentManager] Updating document with modified contents: " + doc_new_string)
            if(prev_document_string == doc_new_string):
                self.logger.log("[DocumentManager] Original document and new document are the same! NOT updating")
            else:
                store_response = self.store.put(document)
                return store_response.status_code

    def remove_document(self, **keys):
        self.logger.log("[DocumentManager] Remove_document. Keys '{0}'".format(keys))
        keys = self._process_document_keys(keys)

        self.logger.log("[DocumentManager] Checking if document already exists")
        doc_obj = self.get_document(**keys)
        if doc_obj is None:
            self.logger.log("[DocumentManager] No document found or already deleted. Nothing to do.")
        else:
            doc_org_string = json.dumps(doc_obj)
            self.logger.log("[DocumentManager] Removing document with concent '{}' ".format(doc_org_string))
            keys['file'] = doc_obj
            store_response = self.store.delete(**keys)
            self.logger.log("[DocumentManager] status: {0}. Reason: {1}".format(store_response.status_code,store_response.reason))
            if store_response.status_code == 200:
                self.logger.log("[DocumentManager] Document REMOVED.")
            else:
                self.logger.log("[DocumentManager] Document was NOT removed.")
        return store_response.status_code
    
    # Method processes and checks document keys.
    # Supports fuzzy get - trying to determine keys from other keys
    def _process_document_keys(self, keys):
        # process to lowercase
        keys = {k.lower() if isinstance(k, str) else k : v.lower() if isinstance(v, str) else v for k, v in keys.items()}

        if not keys.get("category", None):
            type_name = keys.get("type","none") 
            if type_name in types_configs:
                keys["category"] = "configs"
            elif type_name in types_items:
                keys["category"] = "items"
            else:
                raise InvalidDocTypeError(type_name)
        if not keys.get("type", None):
            document_name = keys.get("document_name", "none")
            derived_type_from_name_list = [poss_type for poss_type in types if poss_type in document_name]
            if len(derived_type_from_name_list) == 1:
                keys["type"] = derived_type_from_name_list[0]
            else:
                raise InvalidDocNameError(document_name)

        self.logger.log("[DocumentManager] _process_document_keys. Post Process Keys '{0}'".format(keys))
        return keys
