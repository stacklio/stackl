from handlers.ansible_handler import AnsibleHandler
from handlers.packer_handler import PackerHandler
from handlers.terraform_handler import TerraformHandler


class ToolFactory:

    #TODO what if tool not any of the three?
    def get_handler(self, tool):
        if tool == "terraform":
            return TerraformHandler()
        elif tool == "ansible":
            return AnsibleHandler()
        elif tool == "packer":
            return PackerHandler()
