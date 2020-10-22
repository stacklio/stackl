"""
Abstract class for implementation of all handler classes
"""

from abc import ABC, abstractmethod


class Handler(ABC):  # pylint: disable=too-few-public-methods
    """
    Abstract Handler class for all handlers in Stackl
    """

    def __init__(self):
        pass

    @abstractmethod
    def handle(self, item):
        """
        This method is for the handle logic
        """
        return None
