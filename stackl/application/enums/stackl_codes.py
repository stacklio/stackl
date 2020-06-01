from enum import IntEnum, unique


# Modeled after HTTP Status Codes
@unique
class StatusCode(IntEnum):

    CONTINUE = 100  # Informational response: request was received and understood

    OK = 200  # Success Response: request was a success and the response depends on it
    CREATED = 201  # Success Response: request was a success and a document has been created
    ACCEPTED = 202  # Success Response: request was a success and is in progress

    BAD_REQUEST = 400  # Client Error: the request was not processed due to a client-side error (e.g., invalid syntax, too large, ...)
    UNAUTHORIZED = 401  # Client Error: authentication is required but has failed or has not yet been provided
    FORBIDDEN = 403  # Client Error: Client is not authorized to do the request
    NOT_FOUND = 404  # Client Error: The request is not found
    CONFLICT = 409  # Client Error: The request conflicts with the state of the server
    ROLLBACKED = 410  # Client Error: The request conflicts with the state of the server
    
    INTERNAL_ERROR = 500  # Server Error: STACKL has encountered an error it does not know how to handle.

    @classmethod
    def isSuccessful(cls, code):
        if isinstance(code, StatusCode):
            return 200 <= code.value < 400
        else:
            return 200 <= code < 400
