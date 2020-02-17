import logging

logger = logging.getLogger(__name__)
from manager import Manager


class UserManager(Manager):

    def __init__(self, manager_factory):
        super(UserManager, self).__init__(manager_factory)

        self.document_manager = manager_factory.get_document_manager()

    def get_user_for_cert(self, user_certificate):
        serial = user_certificate['user_serial']
        if serial is None:
            return "default"  # TODO: this is temporary to allow everybody access
        logger.info("[UserManager] get_user_for_cert. Getting user for certificate '{0}'".format(user_certificate))
        user_data = self.document_manager.get_document(type='authentication', document_name=str(serial))
        if user_data:
            return user_data['user']
        else:
            return "default"  # TODO: this is temporary to allow everybody access
            # raise Unauthorized()

    def get_user_for_serial(self, serial):
        logger.info("[UserManager] get_user_for_serial. Getting user for serial '{0}'".format(serial))
        user_data = self.document_manager.get_document(type='authentication', document_name=str(serial))
        if user_data:
            return user_data
        else:
            return "default"  # TODO: this is temporary to allow everybody access
            # raise Unauthorized()

    def create_user(self, user_data):
        if 'role' in user_data and user_data['role'] in ['user', 'automation-endpoint', 'agent']:
            serial = user_data.get('serial', None)
            user_data['type'] = 'user'
            user_data['name'] = user_data['type'] + "_" + serial

            user_doc = self.document_manager.get_document(type='authentication', document_name=str(serial))
            if user_doc:
                raise Exception("[UserManager] The requested user already exists, not creating")
            logger.info("[UserManager] create_user. Creating new user with data {}".format(user_data))

            self.document_manager.write_document(type="authentication", document_name=user_data['serial'],
                                                 file=user_data, description=user_data['description'])
        else:
            raise Exception("[UserManager] The requested user does not contain valid data")

    def delete_user(self, serial):
        user_doc = self.document_manager.get_document(type='authentication', document_name=str(serial))
        if user_doc:
            logger.info("[UserManager] delete_user. Removing user from authourised callers...")
            self.document_manager.remove_document(document_name=serial, type='authentication')
        else:
            raise Exception('[UserManager] User was not found and thus not removed')

    def get_user_auth(self, user_certificate):
        serial = user_certificate['user_serial']
        logger.info("[UserManager] serial: " + str(serial))
        if serial is not None:
            user_doc = self.get_user_for_cert(user_certificate)
            if user_doc and 'role' in user_doc and user_doc['role'] == 'agent':
                return_obj = {'tags': user_doc.get('tags', None)}
                return return_obj
        else:
            # TODO We need to improve and correct authentication. Due to the LFS, at the moment we spoof the system a bit
            return_obj = {'tags': ["common", "tom", "sven", "frederic"]}
            return return_obj

    def get_users(self):
        documents = self.document_manager.get_document(type="authentication")
        if documents:
            return documents
        else:
            return None
