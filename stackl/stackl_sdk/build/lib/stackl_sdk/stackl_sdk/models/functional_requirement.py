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


class FunctionalRequirement(object):
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
        'name': 'str',
        'category': 'str',
        'type': 'str',
        'params': 'object',
        'description': 'str',
        'invocation': 'Invocation'
    }

    attribute_map = {
        'name': 'name',
        'category': 'category',
        'type': 'type',
        'params': 'params',
        'description': 'description',
        'invocation': 'invocation'
    }

    def __init__(self, name=None, category=None, type='functional_requirement', params=None, description='Base Document', invocation=None):  # noqa: E501
        """FunctionalRequirement - a model defined in Swagger"""  # noqa: E501
        self._name = None
        self._category = None
        self._type = None
        self._params = None
        self._description = None
        self._invocation = None
        self.discriminator = None
        self.name = name
        self.category = category
        if type is not None:
            self.type = type
        if params is not None:
            self.params = params
        if description is not None:
            self.description = description
        self.invocation = invocation

    @property
    def name(self):
        """Gets the name of this FunctionalRequirement.  # noqa: E501


        :return: The name of this FunctionalRequirement.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this FunctionalRequirement.


        :param name: The name of this FunctionalRequirement.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def category(self):
        """Gets the category of this FunctionalRequirement.  # noqa: E501


        :return: The category of this FunctionalRequirement.  # noqa: E501
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category):
        """Sets the category of this FunctionalRequirement.


        :param category: The category of this FunctionalRequirement.  # noqa: E501
        :type: str
        """
        if category is None:
            raise ValueError("Invalid value for `category`, must not be `None`")  # noqa: E501

        self._category = category

    @property
    def type(self):
        """Gets the type of this FunctionalRequirement.  # noqa: E501


        :return: The type of this FunctionalRequirement.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this FunctionalRequirement.


        :param type: The type of this FunctionalRequirement.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def params(self):
        """Gets the params of this FunctionalRequirement.  # noqa: E501


        :return: The params of this FunctionalRequirement.  # noqa: E501
        :rtype: object
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this FunctionalRequirement.


        :param params: The params of this FunctionalRequirement.  # noqa: E501
        :type: object
        """

        self._params = params

    @property
    def description(self):
        """Gets the description of this FunctionalRequirement.  # noqa: E501


        :return: The description of this FunctionalRequirement.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this FunctionalRequirement.


        :param description: The description of this FunctionalRequirement.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def invocation(self):
        """Gets the invocation of this FunctionalRequirement.  # noqa: E501


        :return: The invocation of this FunctionalRequirement.  # noqa: E501
        :rtype: Invocation
        """
        return self._invocation

    @invocation.setter
    def invocation(self, invocation):
        """Sets the invocation of this FunctionalRequirement.


        :param invocation: The invocation of this FunctionalRequirement.  # noqa: E501
        :type: Invocation
        """
        if invocation is None:
            raise ValueError("Invalid value for `invocation`, must not be `None`")  # noqa: E501

        self._invocation = invocation

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
        if issubclass(FunctionalRequirement, dict):
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
        if not isinstance(other, FunctionalRequirement):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
