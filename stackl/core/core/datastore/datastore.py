"""
Module for everything containing datastores
"""
from abc import ABC, abstractmethod

from core.enums.stackl_codes import StatusCode


class DataStore(ABC):
    """Abstract class for implementing a datastore"""

    @abstractmethod
    def get(self, **keys):
        """abstractmethod for getting a document"""

    @abstractmethod
    def put(self, file):
        """Abstract method for saving a document"""

    @abstractmethod
    def delete(self, **keys):
        """Abstract method for deleting a document"""

    def _create_store_response(self,
                               status_code=StatusCode.OK,
                               reason=None,
                               content=None):
        """Helper method for creating a store response"""
        response = self.StoreResponse()
        response.status_code = status_code
        response.reason = reason
        response.content = content
        return response

    class StoreResponse:
        """
        The :class:`StoreResponse <StoreResponse>` object,
        which contains a Store's response to a request. Modelled on the HTTP Response.
        Potentially other interesting attributes can be added from HTTP, such as elapsed,
        encoding, etc.
        """

        __attrs__ = ['content', 'status_code', 'reason']

        def __init__(self):
            self.content = False

            #: Integer Code of responded StoreResponse, with direct correlation
            # to HTTP Status, e.g. 404 or 200.
            self.status_code = None

            #: Textual reason of responded StoreResponse, e.g. "Not Found" or "OK".
            self.reason = None

        def __repr__(self):
            return '<StoreResponse. Status Code: {0}. Reason: {1}. Content: {2}>' \
                .format(self.status_code, self.reason, self.content)
