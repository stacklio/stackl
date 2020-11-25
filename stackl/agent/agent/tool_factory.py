"""
Module for ToolFactory
"""
from abc import ABC, abstractmethod


class ToolFactory(ABC):
    """
    Class which contains all methods that a ToolFactory has to implement
    """
    @abstractmethod
    def get_handler(self, invoc):
        """
        Returns the handler for the chosen tool
        """
