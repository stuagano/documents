import unittest
import tkinter as tk
from tkinter import filedialog
from unittest.mock import patch

from pdf_processor.GUI.simple_ui import SimpleUI


class TestSimpleUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.ui = SimpleUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_widgets_exist(self):
        self.assertIsNotNone(self.ui.browse_button)
        self.assertIsNotNone(self.ui.file_label)
        self.assertIsNotNone(self.ui.process_button)
        self.assertIsNotNone(self.ui.status_label)

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_button(self, mock_askopenfilename):
        mock_askopenfilename.return_value = '/path/to/file.pdf'
        self.ui.browse_button.invoke()
        self.assertEqual(self.ui.file_path.get(), '/path/to/file.pdf')
        self.assertEqual(self.ui.file_label.cget('text'), 'Selected File: /path/to/file.pdf')

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_button_cancel(self, mock_askopenfilename):
        mock_askopenfilename.return_value = ''
        self.ui.browse_button.invoke()
        self.assertEqual(self.ui.file_path.get(), '')
        self.assertEqual(self.ui.file_label.cget('text'), 'Selected File: ')

    @patch('pdf_processor.GUI.simple_ui.process_documents')
    def test_process_button(self, mock_process_documents):
        self.ui.file_path.set('/path/to/file.pdf')
        self.ui.process_button.invoke()
        mock_process_documents.assert_called_once_with('/path/to/file.pdf')
        self.assertEqual(self.ui.status_label.cget('text'), 'Processing...')

    @patch('pdf_processor.GUI.simple_ui.process_documents')
    def test_process_button_no_file(self, mock_process_documents):
        self.ui.process_button.invoke()
        mock_process_documents.assert_not_called()
        self.assertEqual(self.ui.status_label.cget('text'), 'Please select a file first.')

    @patch('pdf_processor.GUI.simple_ui.process_documents')
    def test_process_button_error(self, mock_process_documents):
        mock_process_documents.side_effect = Exception('Test Exception')
        self.ui.file_path.set('/path/to/file.pdf')
        self.ui.process_button.invoke()
        self.assertEqual(self.ui.status_label.cget('text'), 'Error: Test Exception')

    @patch('pdf_processor.GUI.simple_ui.process_documents')
    def test_process_button_success(self, mock_process_documents):
        self.ui.file_path.set('/path/to/file.pdf')
        self.ui.process_button.invoke()
        self.assertEqual(self.ui.status_label.cget('text'), 'Processing completed successfully!')