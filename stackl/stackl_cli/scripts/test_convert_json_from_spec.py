#!/usr/bin/python3
import unittest
from convert_json_from_spec import JsonConverter


json_doc = """
{
    "format_version": "0.1",
    "terraform_version": "0.12.20",
    "values": {
        "outputs": {
            "hosts": {
                "sensitive": false,
                "value": [
                    "10.10.4.171"
                ]
            }
        }
    }
}
"""

spec_doc = """
{
    "hosts": "values.outputs.hosts.value"
}
"""

class TestJsonConverter(unittest.TestCase):

    def generic_test_main(self, readme, terraform_variables,
                          terraform_outputs, expected_exception):
        mock_readme = mock.mock_open(read_data=readme)
        mock_readme_2 = mock.mock_open(read_data=readme)
        mock_tf_vars = mock.mock_open(read_data=terraform_variables)
        mock_tf_outputs = mock.mock_open(read_data=terraform_outputs)
        side_effect = [mock_readme.return_value, mock_readme_2.return_value,
                       mock_tf_vars.return_value, mock_tf_outputs.return_value]
        mock_opener = mock.mock_open()
        mock_opener.side_effect = side_effect
        with mock.patch('builtins.open', mock_opener):
            with mock.patch('sys.argv', ['-f']):
                with self.assertRaises(expected_exception):
                    target.main()


    def test_convert(self):
        mock_open = mock.mock_open(read_data=json_doc)
        with mock.patch('builtins.open', mock_open):



        converter = JsonConverter()
