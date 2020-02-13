from flask import request
from flask_restplus import Namespace, fields

from api import StacklApiResource, logger
from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory

api = Namespace('users', description='Operations related to STACKL Users')

user_manager = ManagerFactory().get_user_manager()

users_field = api.model('Users', {
    'role': fields.String(required=True, description='Role of the user (user, automation-endpoint or agent)',
                          example="user"),
    'description': fields.String(required=True, description='Description of the new user', example="Key of <<user>>"),
    'serial': fields.String(required=True, description='Serial of the user certificate', example="00"),
    'fingerprint': fields.String(required=False, description='Fingerprint of the user certificate',
                                 example="0000000000000")
})


@api.route('', strict_slashes=False)
class Users(StacklApiResource):
    def get(self):
        """Returns all users"""
        logger.info("[Users GET] Received GET for users")
        users_list = user_manager.get_users()
        return {"users": users_list}, StatusCode.OK

    @api.expect(users_field, validate=True)
    def post(self):
        """Creates a new user"""
        logger.info("[Users POST] Received POST request for user")
        # extract post data from request
        json_data = request.get_json()
        logger.info("[Users POST] User json_data: {}".format(json_data))
        try:
            user_manager.create_user(json_data)
            return {'return_code': StatusCode.CREATED, 'message': 'Created'}, StatusCode.CREATED
        except Exception as e:
            return {'return_code': StatusCode.CONFLICT, 'message': 'Error: {}'.format(e)}, StatusCode.CONFLICT


@api.route('/<serial>', strict_slashes=False)
class UsersSpecific(StacklApiResource):
    def get(self, serial):
        """Returns a user with a specific serial"""
        logger.info("[UsersSpecific GET] Received GET request for user serial {0}".format(serial))
        return user_manager.get_user_for_serial(serial), 200

    @api.response(StatusCode.ACCEPTED, 'Deletes a user')
    def delete(self, serial):
        """Delete a user with specific serial"""
        logger.info("[UsersSpecific DELETE] Received DELETE request for user " + str(serial))
        try:
            user_manager.delete_user(serial)
            return {'return_code': StatusCode.ACCEPTED, 'message': 'User marked for delete'}, StatusCode.ACCEPTED
        except Exception as e:
            return {'return_code': StatusCode.CONFLICT, 'message': 'Error: {}'.format(e)}, StatusCode.CONFLICT
