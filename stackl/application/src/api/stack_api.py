import logging

from flask import request
from flask_restplus import Namespace, fields, reqparse

from api import StacklApiResource
from enums.stackl_codes import StatusCode

logger = logging.getLogger(__name__)
from manager.manager_factory import ManagerFactory
from task.stack_task import StackTask
from task_broker.task_broker_factory import TaskBrokerFactory

api = Namespace('stack', description='Operations related to STACKL Stacks')

manager_factory = ManagerFactory()
document_manager = manager_factory.get_document_manager()
user_manager = manager_factory.get_user_manager()
stack_manager = manager_factory.get_stack_manager()
task_broker_factory = TaskBrokerFactory()
task_broker = task_broker_factory.get_task_broker()

force_arguments = reqparse.RequestParser()
force_arguments.add_argument('force', type=str, required=False, choices=['True'])

stack_instance_name_field = api.model('stack_instance_name_field', {
    'stack_instance_name': fields.String(required=True, description='Name for the stack instance',
                                         example="web_example_stack1")
})
stack_instance_invoke_field = api.model('stack_instance_invoke_field', {
    'parameters': fields.Raw(required=True, description='Input parameters used for creating the stack instace',
                             example={"key": "value"}),
    'infrastructure_template_name': fields.String(required=True,
                                                  description='The stack infrastructure template to use for the stack instance',
                                                  example="stack_infrastructure_template_demo_example"),
    'application_template_name': fields.String(required=True,
                                               description='The stack application template to use for the new stack instance',
                                               example="stack_application_template_web_example"),
    'stack_instance_name': fields.String(required=False, description='Name for the new stack instance',
                                         example="web_example_stack1")
})


@api.route('/instances/<stack_instance_name>', strict_slashes=False)
class StackInstancesName(StacklApiResource):
    def get(self, stack_instance_name="Example_Instance1"):
        """Returns a stack instance with a specific name"""
        logger.info(
            "[StackInstancesName GET] Getting document for stack instance " + stack_instance_name + ' using manager')
        stack_instance = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
        if not stack_instance:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'Stack instance ' + str(stack_instance_name) + ' not found'}, StatusCode.NOT_FOUND
        return stack_instance

    @api.response(StatusCode.ACCEPTED, 'Stack instance marked for delete')
    @api.expect(force_arguments)
    def delete(self, stack_instance_name="Example_Instance1"):
        """Delete a stack instance with a specific name"""
        logger.info("[StackInstances DELETE] Received DELETE request for " + stack_instance_name)
        stack_instance_exists = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
        if not stack_instance_exists:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'Stack instance ' + str(stack_instance_name) + ' not found'}, StatusCode.NOT_FOUND
        try:
            logger.info("[StackInstances DELETE] force_arguments: " + str(force_arguments.parse_args()))
            force = force_arguments.parse_args()['force']
            logger.info("[StackInstances DELETE] Received POST request with force " + str(force))
            json_data = {}
            json_data['stack_instance_name'] = stack_instance_name
            if force:
                json_data['force'] = force
            task = StackTask({
                'channel': 'worker',
                # 'requester_auth' : requester_auth,
                'json_data': json_data,
                'subtasks': ["DELETE"],
            })
            logger.info("[StackInstances DELETE] Giving StackTask '{0}' to task_broker".format(task.__dict__))
            task_broker.give_task(task)
            return {'return_code': StatusCode.CREATED, 'message': 'Stack instance deleting'}, StatusCode.CREATED
        except Exception as e:
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@api.route('/instances', strict_slashes=False)
class StackInstances(StacklApiResource):
    @api.expect(stack_instance_invoke_field, validate=True)
    def post(self):
        """Creates and invokes a new stack instance with the given name from a stack application template and stack infrastructure template"""
        logger.info("[StackInstances POST] Received POST request")
        json_data = request.get_json()
        logger.info("[StackInstances POST] json_data after get_json: " + str(json_data))
        if not json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: JSON data is mandatory for this POST request'}, StatusCode.BAD_REQUEST
        if 'infrastructure_template_name' not in json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: infrastructure_template_name not found in request data'}, StatusCode.BAD_REQUEST
        if 'application_template_name' not in json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: application_template_name not found in request data'}, StatusCode.BAD_REQUEST
        infr_template_name = json_data['infrastructure_template_name']
        application_template_name = json_data['application_template_name']
        stack_instance_name = json_data['stack_instance_name']

        # check if templates is exists. Should be the case
        infr_template_exists = document_manager.get_document(type="stack_infrastructure_template",
                                                             document_name=infr_template_name)
        logger.info("[StackInstances POST] infr_template_exists (should be the case): " + str(infr_template_exists))
        if not infr_template_exists:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'SIT with name ' + str(infr_template_exists) + ' does not exist'}, StatusCode.NOT_FOUND
        application_template_name = document_manager.get_document(type='stack_application_template',
                                                                  document_name=application_template_name)
        logger.info("[StackInstances POST] application_template_name exists (should be the case): " + str(
            application_template_name))
        if not application_template_name:
            return {'return_code': StatusCode.NOT_FOUND, 'message': 'SAT with name ' + str(
                application_template_name) + ' does not exist'}, StatusCode.NOT_FOUND

        # check if stack_instance already exists. Should not be the case
        stack_instance_exists = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
        logger.info("[StackInstances POST] stack_instance_exists (should not be case): " + str(stack_instance_exists))
        if stack_instance_exists:
            return {'return_code': StatusCode.CONFLICT,
                    'message': 'Stack instance ' + str(stack_instance_name) + ' already exists'}, StatusCode.CONFLICT

        requester_auth = user_manager.get_user_auth(self.request_task.certification_details)
        logger.info("[StackInstances POST] Requester Auth is '{0}".format(requester_auth))

        try:
            task = StackTask({
                'channel': 'worker',
                'requester_auth': requester_auth,
                'json_data': json_data,
                'subtasks': ["CREATE"],
            })
            logger.info("[StackInstances POST] Giving StackTask '{0}' to task_broker".format(task.__dict__))
            task_broker.give_task(task)

            return {'return_code': StatusCode.CREATED, 'message': 'Stack instance creating'}, StatusCode.CREATED
        except Exception as e:
            logger.error("[StackInstances POST] ERROR!!! rest api: " + str(e))
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR

    @api.response(StatusCode.CREATED, 'Stack instance updating')
    @api.expect(stack_instance_invoke_field, validate=True)
    def put(self):
        """Update a stack instance with the given name from a stack application template and stack infrastructure template, creating a new one if it does not yet exist"""
        logger.info("[StackInstances PUT] Received PUT request")
        json_data = request.get_json()
        logger.info("[StackInstances PUT] json_data after get_json: " + str(json_data))
        if not json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: JSON data is mandatory for this POST request'}, StatusCode.BAD_REQUEST
        if 'infrastructure_template_name' not in json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: infrastructure_template_name not found in request data'}, StatusCode.BAD_REQUEST
        if 'application_template_name' not in json_data:
            return {'return_code': StatusCode.BAD_REQUEST,
                    'message': 'Bad request: application_template_name not found in request data'}, StatusCode.BAD_REQUEST
        infr_template_name = json_data['infrastructure_template_name']
        app_template_name = json_data['application_template_name']

        # check if templates is exists. Should be the case
        infr_template_exists = document_manager.get_document(type="stack_infrastructure_template",
                                                             document_name=infr_template_name)
        logger.info("[StackInstances PUT] infr_template_exists (should be the case): " + str(infr_template_exists))
        if not infr_template_exists:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'SIT with name ' + str(infr_template_exists) + ' does not exist'}, StatusCode.NOT_FOUND
        app_template_name = document_manager.get_document(type="stack_application_template",
                                                          document_name=app_template_name)
        logger.info("[StackInstances PUT] app_template_name exists (should be the case): " + str(app_template_name))
        if not app_template_name:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'SAT with name ' + str(app_template_name) + ' does not exist'}, StatusCode.NOT_FOUND

        try:
            task = StackTask({
                'requester_auth': user_manager.get_user_auth(self.request_task.certification_details),
                'channel': 'worker',
                'json_data': json_data,
                'subtasks': ["UPDATE"]
            })
            logger.info("[StackInstances PUT] Giving StackTask '{0}' to task_broker".format(task))
            task_broker.give_task(task)

            return {'return_code': StatusCode.CREATED, 'message': 'Stack instance updating'}, StatusCode.CREATED
        except Exception as e:
            logger.error("[StackInstances PUT] ERROR!!! rest api: " + str(e))
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@api.route('/instances_all', strict_slashes=False)
class StackInstancesAll(StacklApiResource):
    def get(self):
        """Returns all stack instances"""
        logger.info("[StackInstancesAll GET] Returning all stack instances")
        doc = document_manager.get_document(type="stack_instance")
        if doc:
            return doc
        else:
            return {}


@api.route('/templates_all', strict_slashes=False)
class StackTemplatesAll(StacklApiResource):
    def get(self):
        """Returns all stack templates"""
        logger.info("[StackTemplatesAll GET] Returning all Stack templates")
        return document_manager.get_document(type="stack_template")


@api.route('/templates/<stack_template_name>', strict_slashes=False)
class StackTemplate(StacklApiResource):
    def get(self, stack_template_name):
        """Returns a stack template with a specific name"""
        logger.info("[StackTemplate POST] Getting document for stack template " + stack_template_name + ' using manager')
        return document_manager.get_document(type="stack_template", document_name=stack_template_name)


@api.route('/instances/<stack_instance_name>/status', strict_slashes=False)
class StackInstanceStateShort(StacklApiResource):
    def get(self, stack_instance_name):
        """Returns the status for a stack instance with a specific name"""
        logger.info("[StackInstanceStateShort GET] Getting state for stack instance (short) " + stack_instance_name)
        stack_instance_exists = document_manager.get(type="stack_instance", document_name=stack_instance_name)
        if not stack_instance_exists:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'Stack instance ' + str(stack_instance_name) + ' not found'}, StatusCode.NOT_FOUND
        stack_instance_obj_state = stack_manager.get_stack_object_state('types', "stack_instance", stack_instance_name,
                                                                        'short')
        return stack_instance_obj_state


@api.route('/instances/<stack_instance_name>/status/full', strict_slashes=False)
class StackInstanceStateLong(StacklApiResource):
    def get(self, stack_instance_name):
        """Returns the long status for a stack instance with a specific id"""
        logger.info("[StackInstanceStateLong GET] Getting state for stack instance (long) " + stack_instance_name)
        stack_instance_exists = document_manager.get_document(type="stack_instance", document_name=stack_instance_name)
        if not stack_instance_exists:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'Stack instance ' + str(stack_instance_name) + ' not found'}, StatusCode.NOT_FOUND
        stack_instance_obj_state = stack_manager.get_stack_object_state('types', "stack_instance", stack_instance_name,
                                                                        'long')
        return stack_instance_obj_state
