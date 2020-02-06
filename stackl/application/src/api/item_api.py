from flask_restplus import Namespace, fields

from api import StacklApiResource
from enums.stackl_codes import StatusCode
from logger import Logger
from manager.manager_factory import ManagerFactory

api = Namespace('item', description='Operations related to STACKL Item Key/Value Lookups')
logger = Logger("Item API Logger")

document_manager = ManagerFactory().get_document_manager()
item_manager = ManagerFactory().get_item_manager()

item_field = api.model("Item", {
    "item_type": fields.String(required=False, description="Type of the new item", example="infrastructure_target"),
    'input_document1': fields.String(required=False, description="Optional first input document",
                                     example="environment_example1"),
    'input_document2': fields.String(required=False, description="Optional second input document",
                                     example="zone_example1"),
    'input_document3': fields.String(required=False, description="Optional third input document",
                                     example="location_example1")
})


@api.route('/<item_name>', strict_slashes=False)
@api.route('/<item_type>/<item_name>', strict_slashes=False)
class KeyValueItemAll(StacklApiResource):
    def get(self, item_name, item_type=None):
        """Returns all key-value pairs for an item where the type can be derived"""
        try:
            logger.info("[KeyValueItemAll GET] Getting Key/Value pairs for item '{0}'".format(item_name))

            item = document_manager.get_document(category='items', type=item_type, document_name=item_name)
            if not item:
                return {'return_code': StatusCode.NOT_FOUND,
                        'message': 'Item {0} with type {1} not found'.format(item_name,
                                                                             item_type)}, StatusCode.NOT_FOUND
            else:
                return item
        except Exception as e:
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@api.route('/key_value/<item_name>/<key>', strict_slashes=False)
@api.route('/key_value/<item_type>/<item_name>/<key>', strict_slashes=False)
class KeyValueItem(StacklApiResource):
    def get(self, item_name, key, item_type=None):
        """Returns specific key-value pair for a specific item where the type can be derived"""
        try:
            item = document_manager.get_document(category='items', type=item_type, document_name=item_name)
            if not item:
                return {'return_code': StatusCode.NOT_FOUND,
                        'message': 'Item {0} with type {1} not found'.format(item_name,
                                                                             item_type)}, StatusCode.NOT_FOUND
            return item_manager.get_key_value(item, key)
        except Exception as e:
            logger.error("[KeyValueItem GET] EXCEPTION in REST: " + str(e))
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@api.route('/all/<item_type>', strict_slashes=False)
class KeyValueAllItemsOfType(StacklApiResource):
    def get(self, item_type):
        """Returns all key-value pairs for all items of type"""
        try:
            logger.info("[KeyValueAllItems GET] getting all items of type: {}".format(item_type))
            return document_manager.get_document(category='items', type=item_type)
        except Exception as e:
            logger.error("[KeyValueAllItems GET] EXCEPTION in REST: {}".format(str(e)))
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR


@api.route('/create/<item_name>', strict_slashes=False)
class KeyValueCreateItem(StacklApiResource):
    @api.expect(item_field, validate=True)
    def post(self, item_name):
        """Creates an item with the given name from the given other documents (Work-In-Progress)"""
        try:
            logger.info("[KeyValueCreateItem POST] getting all items of type: {}".format(item_name))
            return document_manager.get_document(category='items', type=None, document_name=item_name)
        except Exception as e:
            logger.error("[KeyValueCreateItem POST] EXCEPTION in REST: {}".format(str(e)))
            return {'return_code': StatusCode.INTERNAL_ERROR,
                    'message': 'Internal server error: {}'.format(str(e))}, StatusCode.INTERNAL_ERROR
