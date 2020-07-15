from .handlers.mock_handler import MockHandler
from ..tool_factory import ToolFactory


class MockToolFactory(ToolFactory):
    def get_handler(self, invoc):
        if invoc.tool == "terraform":
            return MockHandler(invoc)
        elif invoc.tool == "ansible":
            return MockHandler(invoc)
        elif invoc.tool == "packer":
            return MockHandler(invoc)
        else:
            raise ValueError(
                "[ToolFactory] Tool '{}' is not recognized".format(
                    invoc["tool"]))
