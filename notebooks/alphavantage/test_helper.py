import unittest
from unittest.mock import patch, MagicMock, mock_open
from helper import fetch_and_save

# Test class for load_config function
# Test class for fetch_and_save function
class TestFetchAndSave(unittest.TestCase):

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)  # Mock file opening
    @patch("json.dump")  # Mock json.dump to prevent actual file writing
    def test_fetch_and_save_success(self, mock_json_dump, mock_open_file, mock_get):
        # Setup the mock response object with a successful status code
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'key': 'value'}  # Mocked JSON data
        mock_get.return_value = mock_response

        # Call the function with test data
        fetch_and_save('AAPL', 'INCOME_STATEMENT', 'test_api_key')

        # Check that requests.get was called with the correct parameters
        mock_get.assert_called_once_with(
            'https://www.alphavantage.co/query',
            params={'function': 'INCOME_STATEMENT', 'symbol': 'AAPL', 'apikey': 'test_api_key'}
        )

        # Check that the file was opened with the correct name
        mock_open_file.assert_called_once_with('../../data/fundamental/AAPL-INCOME_STATEMENT.json', 'w')

        # Check that json.dump was called with the expected data
        mock_json_dump.assert_called_once_with({'key': 'value'}, mock_open_file(), indent=4)

# Run the unit test
if __name__ == '__main__':
    unittest.main()
