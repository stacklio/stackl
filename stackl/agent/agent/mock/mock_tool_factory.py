"""
Tool factory module for testing/debugging purposes
"""
from .handlers.mock_handler import MockHandler
from ..tool_factory import ToolFactory


class MockToolFactory(ToolFactory):
    """
    Mock Tool factory, only used for testing
    """
    def get_handler(self, invoc):
        if invoc.tool == "terraform":
            return MockHandler(invoc)
        if invoc.tool == "ansible":
            return MockHandler(invoc)
        if invoc.tool == "packer":
            return MockHandler(invoc)
        raise ValueError("[ToolFactory] Tool '{}' is not recognized".format(
            invoc["tool"]))
