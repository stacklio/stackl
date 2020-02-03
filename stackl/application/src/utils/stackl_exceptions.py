import sys
sys.path.append('/etc/changes/')

class InvalidDocTypeError(Exception):
    """ Basic exception for when a document is requested with an invalid type"""
    def __init__(self, invalid_type_name, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "The requested document's type '{}' is not  a valid type".format(invalid_type_name)
        super(InvalidDocTypeError, self).__init__(msg)
        self.invalid_type_name = invalid_type_name
        self.msg = msg


class InvalidDocNameError(Exception):
    """ Basic exception for when a document is requested with an invalid name"""
    def __init__(self, invalid_document_name, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "The document with the given name '{}' cannot be resolved into a store understandable format".format(invalid_document_name)
        super(InvalidDocNameError, self).__init__(msg)
        self.invalid_document_name = invalid_document_name
        self.msg = msg
