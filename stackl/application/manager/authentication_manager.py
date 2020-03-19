import logging
import os

logger = logging.getLogger("STACKL_LOGGER")
from manager import Manager

##TODO: Deprecate. This should be handled in a future stage by OPA
class AuthenticationManager(Manager):

    def __init__(self, manager_factory):
        super(AuthenticationManager, self).__init__(manager_factory)

        self.document_manager = manager_factory.document_manager

    def get_tenant(self, client_certificate_details):
        return os.getenv('TENANT_NAME', 'nubera')
        #######################################################################################
        # This was the old implementation, we are not going to use this anymore for the moment
        #######################################################################################
        # serial = client_certificate_details['client_serial']
        # logger.info("[AuthenticationManager] Getting tenant authorisation with serial '{0}'".format(serial) )
        # auth_doc = self.get_auth_document(client_certificate_details)
        # if auth_doc and 'tenant' in auth_doc:
        #     return auth_doc['tenant']
        # else:
        #     raise Unauthorized()

    def get_clients(self, tenant, serial=None, client_role=None):
        view_doc = 'client'
        if client_role:
            view_doc = client_role
        return_object = {"result": []}
        if serial:
            serial = str(serial)
        auth_doc = self.document_manager.get_document('authentication', category='authentication', subcategory=view_doc,
                                                      document_name=serial)
        if auth_doc:
            if isinstance(auth_doc, list):
                auth_docs = auth_doc
            else:
                auth_docs = [auth_doc]
            for auth_doc_tmp in auth_docs:
                if 'tenant' in auth_doc_tmp and auth_doc_tmp['tenant'] == tenant:
                    if not client_role or ("role" in auth_doc_tmp and auth_doc_tmp['role'] == client_role):
                        return_object['result'].append(auth_doc_tmp)
        if serial:
            return return_object['result'][0]
        return return_object

    def create_client(self, tenant, client_data):
        if 'role' in client_data and client_data['role'] in ['administrator', 'automation-endpoint', 'agent']:
            if not client_data.get('serial', None):
                serial = client_data['serial'].upper()
            client_data['type'] = 'client'
            client_data['tenant'] = tenant
            client_data['name'] = serial
            logger.info(
                "[AuthenticationManager] Trying to create new client for tenant " + tenant + " with data " + str(
                    client_data))
            self.document_manager.write_document('authentication', document_name=client_data['serial'],
                                                 subcategory='client', file=client_data,
                                                 description=client_data['description'], category='authentication')
        else:
            raise Exception(
                '[AuthenticationManager] Unsupported role! Must be administrator, automation-endpoint or agent!')

    def delete_client(self, tenant, serial):
        auth_doc = self.document_manager.get_document('authentication', category='authentication', subcategory='client',
                                                      document_name=str(serial))
        if auth_doc:
            if ('tenant' not in auth_doc) or ('tenant' in auth_doc and tenant == auth_doc['tenant']):
                logger.info("[AuthenticationManager] Trying to remove client from authentication DB...")
                self.document_manager.remove_document('authentication', document_name=serial, subcategory='client',
                                                      category='authentication')
            else:
                raise Exception('[AuthenticationManager] Tenant did not match client tenant')

    def get_auth_document(self, client_certificate_details):
        serial_in = client_certificate_details['client_serial']
        serials = [
            serial_in.upper(),
            serial_in.lower(),
        ]
        for serial in serials:
            auth_doc = self.document_manager.get_document('authentication', category="authentication",
                                                          subcategory="client", document_name=str(serial))
            if auth_doc:
                return auth_doc
        # if upper or lower case serial not found, not authorized
        raise Exception("unauthorized")

    def get_client_auth(self, client_certificate_details):
        serial = client_certificate_details['client_serial']
        logger.info("[AuthenticationManager] serial: " + str(serial))
        if serial is not None:
            auth_doc = self.get_auth_document(client_certificate_details)
            if auth_doc and 'role' in auth_doc and auth_doc['role'] == 'agent':
                return_obj = {'tenant': auth_doc['tenant'], 'tags': auth_doc.get('tags', None)}
                return return_obj
        else:
            # TODO We need to improve and correct authentication. Due to the LFS, at the moment we spoof the system a bit
            return_obj = {'tenant': self.get_tenant(None), 'tags': ["common", "tom", "sven", "frederic"]}
            return return_obj
