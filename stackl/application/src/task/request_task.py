from manager.manager_factory import ManagerFactory
from task import Task


class RequestTask(Task):
    @property
    def valid_subtasks(self):
        return [
            "REQUEST"
        ]

    def __init__(self, request_environment, task_data={}):
        self.request_environment = request_environment
        # Needs to happen after certification details because the request environment needs to be set
        super(RequestTask, self).__init__(task_data)

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'request'
        self.certification_details = self._get_certification_details()
        self.user = ManagerFactory().get_user_manager().get_user_for_cert(self.certification_details)

    def _get_certification_details(self):
        CLIENT_VERIFY = self.request_environment.get('CLIENT_VERIFY', None)
        CLIENT_FINGERPRINT = self.request_environment.get('CLIENT_FINGERPRINT', None)
        CLIENT_CERT = self.request_environment.get('CLIENT_CERT', None)
        CLIENT_SERIAL = self.request_environment.get('CLIENT_SERIAL', None)
        CLIENT_CLIENTCERT = self.request_environment.get('CLIENT_CLIENTCERT', None)

        user_certificate_details = {}
        user_certificate_details['user_verify'] = CLIENT_VERIFY
        user_certificate_details['user_fingerprint'] = CLIENT_FINGERPRINT
        user_certificate_details['user_cert'] = CLIENT_CERT
        user_certificate_details['user_serial'] = CLIENT_SERIAL
        user_certificate_details['user_resource_object'] = CLIENT_CLIENTCERT
        return user_certificate_details
