from handlers.ansible_handler import AnsibleHandler
from handlers.terraform_handler import TerraformHandler


class ToolFactory:
    def get_handler(self, tool):
        if tool == "terraform":
            return TerraformHandler()
        elif tool == "ansible":
            return AnsibleHandler()

