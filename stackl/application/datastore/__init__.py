from abc import ABC, abstractmethod


class DataStore(ABC):

    @property
    @abstractmethod
    def datastore_url(self):
        pass

    @abstractmethod
    def get(self, **keys):
        pass

    @abstractmethod
    def put(self, file):
        pass

    @abstractmethod
    def delete(self, **keys):
        pass

    @abstractmethod
    def get_terraform_statefile(self, statefile_name):
        pass

    @abstractmethod
    def put_terraform_statefile(self, name, statefile):
        pass

    @abstractmethod
    def _check_datastore_exists(self, datastore):
        pass

    def _create_store_response(self, status_code=400, reason=None, content=None):
        response = self.StoreResponse()
        response.status_code = status_code
        response.reason = reason
        response.content = content
        return response

    class StoreResponse():
        """The :class:`StoreResponse <StoreResponse>` object, which contains a
        Store's response to a request. Modelled on the HTTP Response.
        [Design] Potentially other interesting attributes can be added from HTTP, such as elapsed, encoding, etc.
        """

        __attrs__ = [
            'content', 'status_code', 'reason'
        ]

        def __init__(self):
            self.content = False

            #: Integer Code of responded StoreResponse, with direct correlation to HTTP Status, e.g. 404 or 200.
            self.status_code = None

            #: Textual reason of responded StoreResponse, e.g. "Not Found" or "OK".
            self.reason = None

        def __repr__(self):
            return '<StoreResponse. Status Code: {0}. Reason: {1}. Content: {2}>' \
                .format(self.status_code, self.reason, self.content)
