from handlers.terraform_handler import TerraformHandler


class ToolFactory:
    def get_handler(self, tool):
        if tool == "terraform":
            return TerraformHandler()
        else:
            return TerraformHandler()
