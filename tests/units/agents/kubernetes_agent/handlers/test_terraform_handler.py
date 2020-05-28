import unittest
import os
from unittest.mock import patch, MagicMock

target = __import__("terraform_handler")

markdown_example = """

    

"""
invocation_example = dict()


class Invocation():
    def __init__(self):
        self.image = "nexus-dockerint.dome.dev/dome/code/terraform/templates/tf_vm_vmw_win:staging"
        self.infrastructure_target = "vsphere.brussels.vmw-vcenter-01"
        self.stack_instance = "test1"
        self.service = "windows_2019_vmw_vsphere"
        self.functional_requirement = "windows2019"
        self.tool = "terraform"
        self.action = "create"


class TestTerraformHandler(unittest.TestCase):
    def test_method(self):
        self.assertFalse(False)

    @patch.dict(os.environ, {'STACKL_HOST': 'localhost:8080'})
    def test_initiate(self):
        # mock = MagicMock()
        # with patch('kubernetes.config.load_incluster_config',
        #        MagicMock(return_value=0)), \
        #     patch('kubernetes.client.ExtensionsV1beta1Api',
        #           MagicMock(return_value=0),
        #                  MagicMock(return_value=mock)):
        terraformHandler = target.TerraformHandler(Invocation())
        self.assertEqual(type(terraformHandler), target.TerraformHandler)

    # def test_header_count(self):
    #     markdown_linter = self.mock_class_read_file(markdown_example,
    #                                                 target.MarkdownTable)
    #     self.assertEqual(len(markdown_linter.header), 3)

    # def test_missing_markdown(self):
    #     with self.assertRaises(ValueError):
    #         self.mock_class_read_file("""""",
    #                                   target.MarkdownTable)


if __name__ == '__main__':
    unittest.main()
