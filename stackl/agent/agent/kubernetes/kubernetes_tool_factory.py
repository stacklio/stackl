from .handlers.ansible_handler import AnsibleHandler
from .handlers.packer_handler import PackerHandler
from .handlers.terraform_handler import TerraformHandler
from ..tool_factory import ToolFactory


class KubernetesToolFactory(ToolFactory):
    def get_handler(self, invoc):
        if invoc.tool == "terraform":
            return TerraformHandler(invoc)
        elif invoc.tool == "ansible":
            return AnsibleHandler(invoc)
        elif invoc.tool == "packer":
            return PackerHandler(invoc)
        else:
            raise ValueError(
                "[ToolFactory] Tool '{}' is not recognized".format(invoc.tool))
