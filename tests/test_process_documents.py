import unittest
from unittest.mock import patch, mock_open
import json
import os
import sys

# Assuming process_documents.py is in the same directory
# Adjust the import path if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pdf_processor', 'GUI', 'scripts')))
from process_documents import process_documents

class TestProcessDocuments(unittest.TestCase):

    def setUp(self):
        # Create dummy config files
        self.config_files = {
            "clientprofile.json": {"preconditions": ["condition1"], "extractions": []},
            "account_profile_config.json": {"preconditions": ["condition2"], "extractions": []},
        }
        for filename, data in self.config_files.items():
            with open(filename, "w") as f:
                json.dump(data, f)

    def tearDown(self):
        # Clean up the dummy config files
        for filename in self.config_files:
            os.remove(filename)


    @patch('builtins.open', new_callable=mock_open, read_data='test pdf content')
    @patch('process_documents.check_preconditions', return_value=True)
    @patch('process_documents.extract_data_from_pdf', return_value={"data": "extracted"})
    def test_successful_processing(self, mock_extract, mock_preconditions, mock_file):
        result = process_documents("test_pdf.pdf", "clientprofile.json")
        self.assertEqual(result, {"data": "extracted"})
        mock_extract.assert_called_once()
        mock_preconditions.assert_called_once()


    @patch('process_documents.check_preconditions', return_value=False)
    def test_precondition_failure(self, mock_preconditions):
        result = process_documents("test_pdf.pdf", "clientprofile.json")
        self.assertEqual(result, "Preconditions not met")  # Expect specific failure message
        mock_preconditions.assert_called_once()


    def test_invalid_input(self):
        # Test with invalid file or config
        result = process_documents("nonexistent.pdf", "clientprofile.json")
        self.assertIn("Error", result) # Check for an error message

        result = process_documents("test_pdf.pdf", "nonexistent_config.json")
        self.assertIn("Error", result)


    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_open):
        result = process_documents("test_pdf.pdf", "clientprofile.json")
        self.assertIn("Error: File not found", result) # Expect specific file not found error


if __name__ == '__main__':
    unittest.main()