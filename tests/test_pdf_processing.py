
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os

from pdf_processor.pdf_processing import validate_config, read_config, extract_text_from_bbox, process_pdf
from pdf_processor.ui.scripts.config_constants import PAGE_NUMBER, BOXES

class TestPDFProcessing(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    @patch('jsonschema.validate')
    def test_validate_config_valid(self, mock_validate, mock_open):
        validate_config("test_config.json")
        mock_validate.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    @patch('jsonschema.validate', side_effect=jsonschema.exceptions.ValidationError("Invalid config"))
    def test_validate_config_invalid(self, mock_validate, mock_open):
        with self.assertRaises(ValueError):
            validate_config("test_config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_read_config(self, mock_open):
        config = read_config("test_config.json")
        self.assertEqual(config, {"test": "data"})

    @patch('pytesseract.image_to_string', return_value="extracted_text")
    @patch('PIL.Image.Image.crop', return_value=MagicMock())
    def test_extract_text_from_bbox(self, mock_crop, mock_ocr):
        image = MagicMock()
        bbox = (0, 0, 100, 100)
        text = extract_text_from_bbox(image, bbox)
        self.assertEqual(text, "extracted_text")
        mock_crop.assert_called_once_with((0, 0, 100, 100))
        mock_ocr.assert_called_once()

    @patch('pdf_processor.pdf_processing.extract_text_from_bbox', return_value="test")
    @patch('pdf_processor.utils.remove_gridlines_from_image', return_value=MagicMock())
    @patch('pdf_processor.utils.get_pdf_images', return_value=[MagicMock()])
    def test_process_pdf(self, mock_images, mock_remove_gridlines, mock_extract):
        config = {"test_field": {PAGE_NUMBER: 1, BOXES: (0,0,0,0)}}
        data = process_pdf("test.pdf", config, "radio")
        self.assertEqual(data["test_field"], "test")


if __name__ == '__main__':
    unittest.main()
