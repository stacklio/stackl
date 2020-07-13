from abc import ABC, abstractmethod

from stackl.enums.stackl_codes import StatusCode


class DataStore(ABC):
    @abstractmethod
    def get(self, **keys):
        pass

    @abstractmethod
    def put(self, file):
        pass

    @abstractmethod
    def delete(self, **keys):
        pass

    def _create_store_response(self,
                               status_code=StatusCode.OK,
                               reason=None,
                               content=None):
        response = self.StoreResponse()
        response.status_code = status_code
        response.reason = reason
        response.content = content
        return response

    class StoreResponse:
        """The :class:`StoreResponse <StoreResponse>` object, which contains a Store's response to a request. Modelled on the HTTP Response.
        Potentially other interesting attributes can be added from HTTP, such as elapsed, encoding, etc.
        """

        __attrs__ = ['content', 'status_code', 'reason']

        def __init__(self):
            self.content = False

            #: Integer Code of responded StoreResponse, with direct correlation to HTTP Status, e.g. 404 or 200.
            self.status_code = None

            #: Textual reason of responded StoreResponse, e.g. "Not Found" or "OK".
            self.reason = None

        def __repr__(self):
            return '<StoreResponse. Status Code: {0}. Reason: {1}. Content: {2}>' \
                .format(self.status_code, self.reason, self.content)