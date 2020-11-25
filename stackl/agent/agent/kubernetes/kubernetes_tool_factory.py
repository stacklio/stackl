"""
Module for kubernets tool factory
"""
from .handlers.ansible_handler import AnsibleHandler
from .handlers.packer_handler import PackerHandler
from .handlers.terraform_handler import TerraformHandler
from ..tool_factory import ToolFactory


class KubernetesToolFactory(ToolFactory):
    """
    KubernetesToolFactory Class
    """
    def get_handler(self, invoc):
        """
        Returns the right handler for the chosen tool
        """
        if invoc.tool == "terraform":
            return TerraformHandler(invoc)
        if invoc.tool == "ansible":
            return AnsibleHandler(invoc)
        if invoc.tool == "packer":
            return PackerHandler(invoc)
        raise ValueError(
            "[ToolFactory] Tool '{}' is not recognized".format(
                invoc["tool"]))
