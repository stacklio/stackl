"""Module containing custom errors used by stackl"""


class InvalidDocTypeError(Exception):
    """ Basic exception for when a document is requested with an invalid type"""

    def __init__(self, invalid_type_name, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = f"The requested document's type '{invalid_type_name}' is not  a valid type"
        super().__init__(msg)
        self.invalid_type_name = invalid_type_name
        self.msg = msg


class InvalidDocNameError(Exception):
    """ Basic exception for when a document is requested with an invalid name"""

    def __init__(self, invalid_name, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = f"The document with the given name '{invalid_name}'" \
                  f" cannot be resolved into a store understandable format"
        super().__init__(msg)
        self.invalid_name = invalid_name
        self.msg = msg


class NoOpaResultException(Exception):
    """Exception for when OPA cant find a result"""
