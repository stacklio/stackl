from handlers.ansible_handler import AnsibleHandler
from handlers.packer_handler import PackerHandler
from handlers.terraform_handler import TerraformHandler


class ToolFactory:

    def get_handler(self, tool):
        if tool == "terraform":
            return TerraformHandler()
        elif tool == "ansible":
            return AnsibleHandler()
        elif tool == "packer":
            return PackerHandler()
        else
            raise ValueError("[ToolFactory] gTool '{}' is not recognized".format(tool))
