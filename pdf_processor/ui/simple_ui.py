import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QMessageBox, QHBoxLayout, QDialog, QScrollArea, QTableView, QHeaderView, QProgressBar, QGridLayout, QRadioButton, QInputDialog, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QModelIndex
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import importlib.util
import json
import re
import time
import logging
import pandas as pd
from typing import Any
from pdf_processor.logic.pdf_processor import initialize_database, precondition_check, compare_images, extract_data_from_pdf, convert_pdf_to_images
from pdf_processor.ui.backlog_manager import BacklogManager
from pdf_processor.ui.ui_utils import extract_data_from_pdf_with_config, populate_config_combobox, load_and_display_pdf
from pdf_processor.database_manager import DatabaseManager
from utils import image_utils
from PyQt5.QtWidgets import QComboBox

logger = logging.getLogger(__name__)

logging.basicConfig(filename='pdf_processor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SC2_MESSAGES = [
    "Warping in progress...",
    "Constructing Pylons...",
    "Gathering Minerals...",
    "Training Probes...",
    "Researching technology...",
    "Building an army...",
    "Ready to attack!",
    "Reticulating splines...",
]

DATABASE_SCHEMA = {
    'document_name': str,
    'page_number': int,
    'field_name': str,
    'field_value': str,
    'account_number': str,
    'box_x': int,
    'box_y': int,
    'box_width': int,
    'box_height': int,
}

TABLE_EXTRACTED_DATA = "extracted_data"
COL_DOCUMENT_NAME = "document_name"
COL_PAGE_NUMBER = "page_number"
COL_FIELD_NAME = "field_name"
COL_FIELD_VALUE = "field_value"
COL_ACCOUNT_NUMBER = "account_number"
COL_BOX_X = "box_x"
COL_BOX_Y = "box_y"
COL_BOX_WIDTH = "box_width"
COL_BOX_HEIGHT = "box_height"


class SimpleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_image = None
        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        self.database_manager = DatabaseManager()
        self.backlog_manager = BacklogManager(self.database_manager, self)
        print(f"Base directory: {self.base_dir}")
        print(f"Scripts directory: {self.scripts_dir}")
        try:
            if not os.path.exists(self.scripts_dir):
                QMessageBox.warning(self, 'Warning', f'Scripts directory not found at: {self.scripts_dir}')
                return
            self.initUI()
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'File not found during initialization')
            logger.exception("File not found during initialization")
        except OSError:
            QMessageBox.critical(self, 'Error', f'OS error during initialization')
            logger.exception("OS error during initialization")

    def handle_file_io_error(self, error, file_path, operation="read"):
        error_message = f"Error {operation}ing file '{file_path}': {error}"
        logging.error(error_message)
        QMessageBox.critical(self, "File Error", error_message)

    def read_json_file(self, file_path):
