# coding: utf-8

"""
    FastAPI

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class FunctionalRequirementStatus(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'functional_requirement': 'str',
        'status': 'int',
        'error_message': 'str'
    }

    attribute_map = {
        'functional_requirement': 'functional_requirement',
        'status': 'status',
        'error_message': 'error_message'
    }

    def __init__(self, functional_requirement=None, status=None, error_message=None):  # noqa: E501
        """FunctionalRequirementStatus - a model defined in Swagger"""  # noqa: E501
        self._functional_requirement = None
        self._status = None
        self._error_message = None
        self.discriminator = None
        self.functional_requirement = functional_requirement
        self.status = status
        if error_message is not None:
            self.error_message = error_message

    @property
    def functional_requirement(self):
        """Gets the functional_requirement of this FunctionalRequirementStatus.  # noqa: E501


        :return: The functional_requirement of this FunctionalRequirementStatus.  # noqa: E501
        :rtype: str
        """
        return self._functional_requirement

    @functional_requirement.setter
    def functional_requirement(self, functional_requirement):
        """Sets the functional_requirement of this FunctionalRequirementStatus.


        :param functional_requirement: The functional_requirement of this FunctionalRequirementStatus.  # noqa: E501
        :type: str
        """
        if functional_requirement is None:
            raise ValueError("Invalid value for `functional_requirement`, must not be `None`")  # noqa: E501

        self._functional_requirement = functional_requirement

    @property
    def status(self):
        """Gets the status of this FunctionalRequirementStatus.  # noqa: E501


        :return: The status of this FunctionalRequirementStatus.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this FunctionalRequirementStatus.


        :param status: The status of this FunctionalRequirementStatus.  # noqa: E501
        :type: int
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501
        allowed_values = [1, 2, 3]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def error_message(self):
        """Gets the error_message of this FunctionalRequirementStatus.  # noqa: E501


        :return: The error_message of this FunctionalRequirementStatus.  # noqa: E501
        :rtype: str
        """
        return self._error_message

    @error_message.setter
    def error_message(self, error_message):
        """Sets the error_message of this FunctionalRequirementStatus.


        :param error_message: The error_message of this FunctionalRequirementStatus.  # noqa: E501
        :type: str
        """

        self._error_message = error_message

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(FunctionalRequirementStatus, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FunctionalRequirementStatus):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
