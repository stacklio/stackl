import logging

logger = logging.getLogger("STACKL_LOGGER")
from manager import Manager


##TODO TBD: Rework entirely to integrate with OPA, part of the authorisation/authentication rework
class UserManager(Manager):
    def __init__(self):
        super(UserManager, self).__init__()

        self.document_manager = None  #To be given after initalisation by manager_factory

    def handle_task(self, task):
        pass

    def rollback_task(self, task):
        pass

    def get_user_for_cert(self, user_certificate):
        serial = user_certificate['user_serial']
        if serial is None:
            return "default"
        logger.info(
            "[UserManager] get_user_for_cert. Getting user for certificate '{0}'"
            .format(user_certificate))
        user_data = self.document_manager.get_document(type='authentication',
                                                       name=str(serial))
        if user_data:
            return user_data['user']
        else:
            return "default"
            # raise Unauthorized()

    def get_user_for_serial(self, serial):
        logger.info(
            "[UserManager] get_user_for_serial. Getting user for serial '{0}'".
            format(serial))
        user_data = self.document_manager.get_document(type='authentication',
                                                       name=str(serial))
        if user_data:
            return user_data
        else:
            return "default"
            # raise Unauthorized()

    def create_user(self, user_data):
        if 'role' in user_data and user_data['role'] in [
                'user', 'automation-endpoint', 'agent'
        ]:
            serial = user_data.get('serial', None)
            user_data['type'] = 'user'
            user_data['name'] = user_data['type'] + "_" + serial

            user_doc = self.document_manager.get_document(
                type='authentication', name=str(serial))
            if user_doc:
                raise Exception(
                    "[UserManager] The requested user already exists, not creating"
                )
            logger.info(
                "[UserManager] create_user. Creating new user with data {}".
                format(user_data))

            self.document_manager.write_document(
                type="authentication",
                name=user_data['serial'],
                file=user_data,
                description=user_data['description'])
        else:
            raise Exception(
                "[UserManager] The requested user does not contain valid data")

    def delete_user(self, serial):
        user_doc = self.document_manager.get_document(type='authentication',
                                                      name=str(serial))
        if user_doc:
            logger.info(
                "[UserManager] delete_user. Removing user from authourised callers..."
            )
            self.document_manager.delete_document(name=serial,
                                                  type='authentication')
        else:
            raise Exception(
                '[UserManager] User was not found and thus not removed')

    def get_user_auth(self, user_certificate):
        serial = user_certificate['user_serial']
        logger.info("[UserManager] serial: " + str(serial))
        if serial is not None:
            user_doc = self.get_user_for_cert(user_certificate)
            if user_doc and 'role' in user_doc and user_doc['role'] == 'agent':
                return_obj = {'tags': user_doc.get('tags', None)}
                return return_obj
        else:
            return_obj = {'tags': ["common", "tom", "sven", "frederic"]}
            return return_obj

    def get_users(self):
        documents = self.document_manager.get_document(type="authentication")
        if documents:
            return documents
        else:
            return None
