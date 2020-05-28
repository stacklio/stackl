import mock
import unittest


class BaseTest(unittest.TestCase):
    def mock_class_read_file(self, file, mocked_class, **kwargs):
        mock_open = mock.mock_open(read_data=file)
        with mock.patch('builtins.open', mock_open):
            return mocked_class(kwargs)

    def mock_function_read_file(self, file, function):
        mock_open = mock.mock_open(read_data=file)
        with mock.patch('builtins.open', mock_open):
            return function('file')

    def mock_function_read_files(self, file, file2, function):
        mock_open = mock.mock_open(read_data=file)
        with mock.patch('builtins.open', mock_open):
            return function('file')
