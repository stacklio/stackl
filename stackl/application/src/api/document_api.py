from flask import request
from flask_restplus import Namespace, fields, reqparse

from api import StacklApiResource, logger
from enums.stackl_codes import StatusCode
from globals import types
from manager.manager_factory import ManagerFactory
from task.document_task import DocumentTask
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.general_utils import generate_random_string
from utils.stackl_exceptions import InvalidDocTypeError

api = Namespace("documents", description="Operations related to STACKL Documents")

document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()

document_field = api.model("Document", {
    "name": fields.String(required=True, description="Name of the new document", example="optional_name"),
    "type": fields.String(required=True, description="The type of the document", example="environment"),
    'description': fields.String(required=False, description="Description of the new document",
                                 example="A new test document")
})


@api.route('', strict_slashes=False)
class DocumentTypesOverview(StacklApiResource):
    def get(self):
        """Returns all valid types for documents"""
        return types

    @api.response(StatusCode.CREATED, 'Created')
    @api.expect(document_field, validate=True)
    def post(self):
        """Create the document with a specific type and an optional name given in the payload"""
        logger.info("[DocumentByTypeAndName POST] Receiver POST request")
        json_data = request.get_json()
        type_name = json_data["type"]

        document_name = json_data['name']
        if not document_name == "optional_name":
            # check if doc already exists
            try:
                document = document_manager.get_document(type=type_name, document_name=document_name)
                if document:
                    return {'return_code': StatusCode.CONFLICT,
                            'message': "A document with this name for POST already exists"}, StatusCode.CONFLICT
            except InvalidDocTypeError as e:
                return {'return_code': StatusCode.BAD_REQUEST, 'message': e.msg}, StatusCode.BAD_REQUEST
        else:
            document_name = type_name + "_" + generate_random_string()

        document = {'payload': json_data, 'type': type_name, 'name': document_name}

        if 'description' not in json_data:
            document['description'] = 'type ' + \
                                      type_name + ' with name ' + json_data['name']
        else:
            document['description'] = json_data['description']

        task = DocumentTask({
            'channel': 'worker',
            'document': document,
            'subtasks': ["POST_DOCUMENT"]
        })
        logger.info("[DocumentByTypeAndName POST] Giving Document Task '{0}' to task_broker".format(task))
        task_broker.give_task(task)
        return {'return_code': StatusCode.CREATED, 'message': 'Created'}, StatusCode.CREATED


@api.route('/<type_name>', strict_slashes=False)
class DocumentByType(StacklApiResource):
    def get(self, type_name):
        """Returns all documents with a specific type"""
        logger.info("[DocumentsByType GET] Receiver GET request with data: " + type_name)
        try:
            documents = document_manager.get_document(type=type_name)
        except InvalidDocTypeError as e:
            return {'return_code': StatusCode.BAD_REQUEST, 'message': e.msg}, StatusCode.BAD_REQUEST

        logger.info("[DocumentsByType GET] document(s): " + str(documents))
        if documents:
            if type(documents) is list:
                return {"result": documents}
            return {"result": [documents]}
        return {"result": []}


@api.route('/<type_name>/<document_name>', strict_slashes=False)
class DocumentByTypeAndName(StacklApiResource):
    def get(self, type_name, document_name):
        """Returns a specific document with a type and name"""
        logger.info("[DocumentByTypeAndName GET] Receiver GET request with data: " + type_name + " - " + document_name)
        parser = reqparse.RequestParser()
        parser.add_argument('key', help='Get value for a specific key')
        args = parser.parse_args()
        try:
            document = document_manager.get_document(type=type_name, document_name=document_name)
        except InvalidDocTypeError as e:
            return {'return_code': StatusCode.BAD_REQUEST, 'message': e.msg}, StatusCode.BAD_REQUEST

            # Find values if key is passed
        if args['key']:
            key = args['key']
            # check to strip the quotes if passed by the user
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            if key in document:
                return document[key]
            else:
                return {}
        else:
            if document:
                return document
            else:
                return {}

    @api.response(StatusCode.CREATED, 'Updated')
    @api.expect(document_field, validate=True)
    def put(self, type_name, document_name):
        """Updates (or creates) a document with the given type and name"""
        logger.info("[DocumentByTypeAndName PUT] Receiver PUT request with data: " + type_name)
        json_data = request.get_json()

        document = {}
        document['payload'] = json_data
        document['type'] = type_name
        document['name'] = document_name

        if 'description' not in json_data:
            document['description'] = 'type ' + \
                                      type_name + ' with name ' + json_data['name']
        else:
            document['description'] = json_data['description']

        task = DocumentTask({
            'channel': 'worker',
            'return_channel': 'rest',
            'document': document,
            'subtasks': ["PUT_DOCUMENT"]
        })
        logger.info("[TypeWithName PUT] Giving Document Task '{0}' to task_broker".format(task))
        task_broker.give_task(task)
        return {'return_code': StatusCode.CREATED, 'message': 'Updated'}, StatusCode.CREATED

    @api.response(StatusCode.OK, 'Deleted')
    def delete(self, type_name, document_name):
        """Deletes a specific document with a type and name"""
        logger.info(
            "[DocumentByTypeAndName DELETE] Receiver DELETE request with data: " + type_name + " - " + document_name)
        document = document_manager.get_document(type=type_name, document_name=document_name)
        if document:
            task = DocumentTask({
                'channel': 'worker',
                'return_channel': 'rest',
                'document': document,
                'subtasks': ["DELETE_DOCUMENT"]
            })
            task_broker.give_task(task)
            return {'return_code': StatusCode.OK, 'message': 'Document removed successfully!'}, StatusCode.OK
        else:
            return {'return_code': StatusCode.NOT_FOUND,
                    'message': 'Document with type_name ' + str(type_name) + ' and document_name ' + str(
                        document_name) + ' was not found'}, StatusCode.NOT_FOUND
