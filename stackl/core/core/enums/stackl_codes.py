"""Stackl Status Codes module"""
from enum import IntEnum, unique


# Modeled after HTTP Status Codes
@unique
class StatusCode(IntEnum):
    """Enums for stackl codes"""

    CONTINUE = 100  # Informational response: request was received and understood

    OK = 200  # Success Response: request was a success and the response depends on it
    CREATED = 201  # Success Response: request was a success and a document has been created
    ACCEPTED = 202  # Success Response: request was a success and is in progress

    # Client Errors
    BAD_REQUEST = 400  # the request was not processed due to a client-side error (
    UNAUTHORIZED = 401  # authentication is required but has failed or has not yet been provided
    FORBIDDEN = 403  # Client is not authorized to do the request
    NOT_FOUND = 404  # The request is not found
    CONFLICT = 409  # The request conflicts with the state of the server
    ROLLBACKED = 410  # The request conflicts with the state of the server

    # Server Errors
    INTERNAL_ERROR = 500  # STACKL has encountered an error it does not know how to handle.

    @classmethod
    def is_successful(cls, code):
        """checks if status code is between 200 and 400"""
        if isinstance(code, StatusCode):
            return 200 <= code < 400
        return 200 <= code < 400
