# FILE:SIMPLE_UI.PY
import logging
logger = logging.getLogger(__name__)
# FILE:SIMPLE_UI.PY

import sys
import os
import sqlite3

from pdf_processor.ui.ui_utils import *


import json
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QHBoxLayout, QDialog, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import importlib.util

import time
import logging


import pandas as pd
from PyQt5.QtWidgets import QTableView, QHeaderView
from pdf_processor.ui.ui_utils import extract_data_from_pdf_with_config, populate_config_combobox # new import
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QRadioButton

from PyQt5.QtCore import QAbstractTableModel
from typing import Any  # new import

from pdf_processor.pdf_processing import initialize_database, precondition_check, compare_images, extract_data_from_pdf, convert_pdf_to_images

# Set up logging
logging.basicConfig(filename='pdf_processor.log', level=logging.INFO,  # Changed to INFO for more details
                    format='%(asctime)s - %(levelname)s - %(message)s')

# StarCraft 2 themed messages for the progress bar
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

# Define data type mappings for database columns
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

# Constants for table and column names
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


from pdf_processor.ui.backlog_models import BacklogRecord, BacklogManager
#from pdf_processor.ui.backlog_models import backlog_queue #Remove unnecessary import
#New imports
from pdf_processor.ui.ui_utils import extract_data_from_pdf_with_config, populate_config_combobox, load_and_display_pdf
from pdf_processor.database_manager import DatabaseManager
from utils.image_utils import *
from pdf_processor.ui.backlog_manager import handle_backlog

class BacklogRecord: # Moved from global scope to inside SimpleUI class
    def __init__(self, document_name, page_number, field_name, pdf_path):
        self.document_name = document_name
        self.page_number = page_number
        self.field_name = field_name
        self.pdf_path = pdf_path  # Store the path to the PDF file


class SimpleUI(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory containing simple_ui.py
        # Add current_image attribute to store the loaded image
        self.current_image = None

        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        self.backlog_queue = []  # Initialize the backlog queue
        
        print(f"Base directory: {self.base_dir}")
        print(f"Scripts directory: {self.scripts_dir}")        
        
        self.database_manager = DatabaseManager()
        # Verify scripts directory exists
        if not os.path.exists(self.scripts_dir):
            QMessageBox.warning(self, 'Warning', f'Scripts directory not found at: {self.scripts_dir}')
            return
            
        self.initUI()
        self.backlog_manager = BacklogManager(self.database_manager)  # Instantiate BacklogManager            


    def handle_file_io_error(self, error, file_path, operation="read"):
        """Handles file I/O errors with logging and user feedback."""
        error_message = f"Error {operation}ing file '{file_path}': {error}"
        logging.error(error_message)
        QMessageBox.critical(self, "File Error", error_message)

    def read_json_file(self, file_path):
        """
        Reads a JSON file with error handling and schema extraction.
        
        Returns:
            tuple: A tuple containing the data and a dictionary representing the schema.
                   The schema dictionary maps field names to their data types.
        """
        try:
            with open(file_path, 'r') as file:
                config_data = json.load(file)
                
                schema = {}
                for field in config_data.get('global_fields', []) + list(config_data.values()):
                    if isinstance(field, dict) and 'field_name' in field:
                        data_type = field.get('data_type')
                        if data_type:
                            schema[field['field_name']] = data_type
                
                return config_data, schema
        except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
            self.handle_file_io_error(e, file_path)
            return None

    def load_script_module(self, script_path):
        """Load a Python script module dynamically."""
        try:            
            module_name = os.path.splitext(os.path.basename(script_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            if spec is None:
                raise ImportError(f"Could not load specification for module: {script_path}")
                
            script_module = importlib.util.module_from_spec(spec)
            if script_module is None:
                raise ImportError(f"Could not create module from spec: {script_path}")
            
            spec.loader.exec_module(script_module)
            return script_module
            
        except Exception as e:
            logger.exception("Failed to load script module %s: %s", script_path, e)
            raise ImportError(f"Failed to load script module {script_path}: {str(e)}")

    def initUI(self):
        try:
            self.database_manager = DatabaseManager() # Initialize DatabaseManager
            initialize_database()  # Initialize the database
        except Exception as e:            
            QMessageBox.critical(self, 'Error', f'Database initialization failed: {e}')
            return

        self.setWindowTitle('Simple Script Runner')
        self.setGeometry(100, 100, 1000, 700)  # Increased size for better image viewing

        layout = QVBoxLayout()

        # Script selection
        self.script_label = QLabel('Available Scripts:', self)
        layout.addWidget(self.script_label)
        
        self.script_list = QListWidget(self)
        self.populate_script_list()
        self.script_list.setCurrentRow(0)  # Select the first script by default
        layout.addWidget(self.script_list)

        # Input Directory selection
        input_dir_layout = QHBoxLayout()
        self.input_dir_label = QLabel('Input Directory:', self)
        input_dir_layout.addWidget(self.input_dir_label)
        
        self.input_dir_path = QLabel('Not Selected', self)
        input_dir_layout.addWidget(self.input_dir_path)
        
        self.btn_select_input = QPushButton('Select Input Directory', self)
        self.btn_select_input.clicked.connect(self.select_input_directory)
        input_dir_layout.addWidget(self.btn_select_input)
        
        # Extraction type selection (radio buttons)
        self.extraction_type_label = QLabel('Extraction Type:', self)
        layout.addWidget(self.extraction_type_label)

        self.file_based_radio = QRadioButton('File-Based', self)
        self.database_based_radio = QRadioButton('Database-Based', self)
        self.database_based_radio.setChecked(True)  # Default to database-based
        layout.addWidget(self.file_based_radio)
        layout.addWidget(self.database_based_radio)

        layout.addLayout(input_dir_layout)

        # Output Directory selection
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel('Output Directory:', self)
        output_dir_layout.addWidget(self.output_dir_label)
        
        self.output_dir_path = QLabel('Not Selected', self)
        output_dir_layout.addWidget(self.output_dir_path)
        
        self.btn_select_output = QPushButton('Select Output Directory', self)
        self.btn_select_output.clicked.connect(self.select_output_directory)
        output_dir_layout.addWidget(self.btn_select_output)
        
        layout.addLayout(output_dir_layout)

        # PDF File selection
        pdf_layout = QHBoxLayout()
        self.pdf_label = QLabel('Selected PDF:', self)
        pdf_layout.addWidget(self.pdf_label)
        
        self.pdf_path = QLabel('No PDF Selected', self)
        pdf_layout.addWidget(self.pdf_path)
        
        self.btn_select_pdf = QPushButton('Select PDF File', self)
        self.btn_select_pdf.clicked.connect(self.select_pdf_file)
        pdf_layout.addWidget(self.btn_select_pdf)
        
        layout.addLayout(pdf_layout)

        # Config File selection
        self.config_dir = os.path.join(self.base_dir, 'configs')
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
                QMessageBox.warning(self, 'Warning', f'Configs directory created at: {self.config_dir}')
            except OSError as e:
                QMessageBox.critical(self, 'Error', f'Failed to create configs directory: {e}')
                logger.exception("Failed to create configs directory: %s", e)
                return

        try:
            self.config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')] 
            if not self.config_files:
                self.handle_file_io_error("No config files found", self.config_dir, "listing")
            else:  # This block now correctly executes if config files are found
                config_layout = QHBoxLayout()
                self.config_label = QLabel('Config File:', self)
                config_layout.addWidget(self.config_label)
                self.config_combo_box = QComboBox(self) # Assuming QComboBox is imported
                from PyQt5.QtWidgets import QComboBox
                self.config_combo_box = QComboBox(self)
                config_layout.addWidget(self.config_combo_box)
                layout.addLayout(config_layout)

                # Set the default config file path (This should also be inside the else block)
                try:
                    self.config_file = os.path.join(self.config_dir, self.config_files[0])
                except IndexError:
                    self.handle_file_io_error("No config files to select", self.config_dir, "listing")
                    logging.warning("No config files found to select.")
        except Exception as e:  # Handle potential exceptions during file listing
            QMessageBox.critical(self, "Error", f"An error occurred during config file loading: {e}")
            logger.exception("An error occurred during config file loading: %s", e)       

            # Image display area (Removed from main window)

        # Process PDF button
        self.btn_process = QPushButton('Process PDF', self)
        self.btn_process.clicked.connect(self.process_pdf)
        layout.addWidget(self.btn_process)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate state
        self.progress_bar.setTextVisible(True)  # Show text on the progress bar
        self.progress_message_index = 0  # Index for cycling through messages
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress_message)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Initialize directories and PDF path
        self.input_directory = ''
        self.output_directory = ''
        self.previous_image_path = None  # Store path to previous image
        
        self.pdf_file = ''
        # Add config_file attribute
        self.config_file = '' 
        
        

        self.add_records_button = QPushButton('Add Records to Database', self)
        self.add_records_button.clicked.connect(self.add_records_to_db)
        layout.addWidget(self.add_records_button)

        # View Data button
        self.view_data_button = QPushButton('View Extracted Data', self)
        self.view_data_button.clicked.connect(self.view_extracted_data)
        layout.addWidget(self.view_data_button)

        # Backlog Queue UI
        self.backlog_list = QListWidget(self)
        layout.addWidget(QLabel("Backlog Queue:", self))
        layout.addWidget(self.backlog_list)
        self.review_backlog_button = QPushButton("Review Backlog", self)
        self.review_backlog_button.clicked.connect(self.review_backlog)
        layout.addWidget(self.review_backlog_button)

    def update_progress_message(self):
        """Updates the progress bar message with StarCraft 2 themed messages."""
        # If the progress bar is in indeterminate state (maximum is 0), show rotating messages
        if self.progress_bar.maximum() == 0:
            self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)
        # If the progress bar is in determinate state (maximum > 0), show progress percentage
        else:
            self.progress_bar.setFormat(f"{self.progress_bar.value()}/{self.progress_bar.maximum()} - {SC2_MESSAGES[self.progress_message_index]}")
            self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)        
        self.progress_bar.setFormat(SC2_MESSAGES[self.progress_message_index])
        self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)

    def _insert_record(self, cursor, table_name, record_data, config_schema, pdf_path):
        """Validates and inserts individual records into the database, handling duplicates."""
        account_number = record_data.get('account_number')
        if account_number:
            existing_record = self.database_manager.get_record_by_account_number(account_number)
            if existing_record:
                self.handle_duplicate_account_number(existing_record, record_data)
                cursor = self.database_manager.get_cursor()
                return False

        validated_data = self.validate_and_convert_data_types(record_data, config_schema)
        try:
            columns = ', '.join(validated_data.keys())
            placeholders = ', '.join(['?'] * len(validated_data))
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_sql, tuple(validated_data.values()))
            return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity error for record: {e}")
            return False

    def _update_progress(self, config_index, total_configs, message):
        """Updates the progress bar."""
        self.progress_bar.setValue(config_index)
        self.show_message(message)


    
        """
        Populates the database tables with information from the JSON config files.
        """
        conn = self.database_manager.get_connection()
        cursor = self.database_manager.get_cursor()

        if not self.input_directory or not self.output_directory:
           QMessageBox.warning(self, 'Warning', 'Please select input and output directories.')
        self.progress_bar.setMaximum(len(self.config_files) - 1)  # Exclude all_data_config.json
        self.progress_bar.setValue(0)
        self.progress_timer.start(1000)
        self.show_message("Starting database population...")

        config_index = 0
        try:
            for config_file in self.config_files:
                if config_file != "all_data_config.json":
                    config_path = os.path.join(self.config_dir, config_file)
                    _, config_schema = self.read_json_file(config_path)
                    if config_schema:
                        self._create_database_tables(cursor, config_schema)
                    else:
                        logging.warning(f"No schema found in config file: {config_file}")
                        continue

                    extracted_data = self.backlog_manager.extract_data_from_pdfs(self.input_directory, config_path)

                    for pdf_path, pdf_data in extracted_data.items():
                         for page_number, page_data in pdf_data.items():
                            for field_name, field_value in page_data.items():
                                if field_value is not None:
                                    record_data = {
                                        'document_name': os.path.basename(pdf_path),
                                        'page_number': int(page_number),
                                        'field_name': field_name,
                                        'field_value': field_value,
                                         'account_number': pdf_data.get(1, {}).get('Account Number'), #Assuming account number is on page 1
                                        **{k: v for k, v in page_data.items() if k.endswith('_bbox')}
                                    }
                                    if not self._insert_record(cursor, "completed_records", record_data, config_schema, pdf_path):
                                        self.backlog_manager.add_to_backlog(pdf_path, page_number, field_name)  # Use backlog_manager
                                else:
                                    self.backlog_manager.add_to_backlog(pdf_path, page_number, field_name)  # Use backlog_manager
                    config_index += 1
                    
                    self._update_progress(config_index, len(self.config_files) - 1, f"Processed config: {config_file}")

        except Exception as e:
            logging.exception("Error during database operation: %s", e)
            QMessageBox.critical(self, 'Error', f'An error occurred during database operation: {e}')
            conn.rollback()
        finally:
            if conn:                
                conn.close()
            self.progress_timer.stop()
            self.progress_bar.reset()
            self.show_message("Database population completed!")
        if self.backlog_queue:
            QMessageBox.information(self, "Information: Null Values Detected", "Some records were skipped due to null values. Please review the backlog queue.")            

    def show_message(self, message):
        self.progress_bar.setFormat(SC2_MESSAGES[self.progress_message_index] + " - " + message)
        self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)

    def add_records_to_db(self):
        """Creates database tables if they don't exist and populates them with data."""
        try:
            self.database_manager.create_tables()  # Use DatabaseManager to create tables
            logging.info("Database tables created successfully.")
            self._populate_database()  # Populate the database with extracted data
        except Exception as e:
            logging.exception("Error creating database tables or populating database: %s", e)
            QMessageBox.critical(self, 'Error', f'An error occurred during table creation or database population: {e}')

    def start_progress(self):
        try:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_timer.start(1000)  # Update message every 1000ms (1 second)
            """Displays a message to the user (replace with your preferred method)."""
            print("Progress started")  # Or use QMessageBox, logging, etc.
            self.show_message("Progress started")  # Display a message
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error displaying page: {e}")
            logging.exception(f"Error displaying page: {e}")            


    def display_dataframe_head(self, df):
        """Prints the first 5 rows of the DataFrame to the console."""
        print("DataFrame Head:")
        print(df.head())
        
    def validate_and_convert_data_types(self, data_dict, schema):
        """Validates and converts data types to match the database schema."""
        validated_data = {}
        for field_name, field_value in data_dict.items():
            expected_type = schema.get(field_name) 
            if expected_type is not None:
                if isinstance(field_value, expected_type):
                    validated_data[field_name] = field_value
                else:
                    try:
                        # Attempt type conversion
                        validated_data[field_name] = expected_type(field_value)
                    except (ValueError, TypeError):
                        # Log or handle the error, e.g., skip the record or display a warning
                        logging.warning(f"Type conversion failed for field '{field_name}' in document '{data_dict.get('document_name', 'N/A')}'")
                        # You might choose to set the field to None or a default value
                        validated_data[field_name] = None
            else:
                # If field is not in the schema, include it as is
                validated_data[field_name] = field_value
        return validated_data

    def handle_type_mismatch(self, document_name, field_name, expected_type, actual_value):
        """Handles data type mismatches during data insertion."""
        message = f"Type mismatch for field '{field_name}' in document '{document_name}'. Expected {expected_type}, got {type(actual_value)} ({actual_value}). Skipping record."
        logging.warning(message)
        QMessageBox.warning(self, "Warning", message)

    def populate_script_list(self):
        try:
            if os.path.exists(self.scripts_dir):
                scripts = [f for f in os.listdir(self.scripts_dir) if f.endswith('.py')]
                if scripts:
                    self.script_list.addItems(scripts)
                else:
                    QMessageBox.information(self, 'Info', 'No scripts found in the scripts directory.')
            else:                
                logger.warning("Scripts directory not found: %s", self.scripts_dir)
                QMessageBox.warning(self, 'Warning', f'Scripts directory not found: {self.scripts_dir}')                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading scripts: {e}')
            logger.exception("Error loading scripts: %s", e)

    def select_input_directory(self):        

        directory = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if (directory):
            self.input_directory = directory
            self.input_dir_path.setText(directory)

    def select_output_directory(self):
        
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if (directory):
            self.output_directory = directory

    def extract_to_files(self):
        """
        Performs file-based extraction.
        """
        if not self.input_directory or not self.output_directory:
            QMessageBox.warning(self, 'Warning', 'Please select input and output directories.')
            return

        try:
            for filename in os.listdir(self.input_directory):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(self.input_directory, filename)
                    output_file = os.path.join(self.output_directory, filename[:-4] + ".json")  # Output as JSON

                    # Read config file
                    with open(self.config_file, 'r') as config_f:
                        config_data = json.load(config_f)

                    # Extract data and write to file
                    extracted_data = extract_data_from_pdf_with_config(pdf_path, self.config_file)
                    with open(output_file, 'w') as f:
                        json.dump(extracted_data, f, indent=4)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error during file-based extraction: {e}')
            logger.exception(f"Error during file-based extraction: %s", e)
            return

    def process_pdf(self):
        """Initiates the PDF processing workflow."""
        try:
            self.start_progress()  # Start progress bar
            self.validate_and_run_extraction()
        except ValueError as e:
            QMessageBox.warning(self, 'Warning', str(e))
            logging.warning(str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred during PDF processing: {e}')
            logging.exception(f'An error occurred during PDF processing: {e}')
        finally:
            self.progress_timer.stop()  # Stop progress bar timer
            self.progress_bar.reset()  # Reset progress bar

    def validate_and_run_extraction(self):
        """Validates input and runs either extraction or database import."""
        if not self.input_directory or not self.output_directory or not self.pdf_file or not self.config_file:
            raise ValueError("Please select input directory, output directory, PDF file, and config file.")

        if self.config_file.endswith("all_data_config.json"):
            self.add_records_to_db()  # Call add_records_to_db directly
        else:
            self._run_extraction()  # Run the normal extraction process

    def _run_precondition_check(self, images):
        """Runs the precondition check and handles the results."""
        results = precondition_check(images)
        if not all(results.values()):  # Check if any precondition failed
            raise ValueError("Precondition check failed. Please review the document.")
        return results

    def _extract_data(self):        
        """Extracts data from the PDF using the selected config file."""
        data = extract_data_from_pdf(self.pdf_file, self.config_file)
        return data

    def _handle_image_comparison(self):
        """Handles image comparison logic."""
        if self.previous_image_path:
            previous_image = Image.open(self.previous_image_path)
            if not compare_images(self.current_image, previous_image):
                raise ValueError("Image comparison failed. Extraction cancelled.")
        return True  # Indicate continuation

    def _run_extraction(self):        
        """Performs the extraction process."""
        try:
            selected_script_item = self.script_list.currentItem()
            if not selected_script_item:
                raise ValueError('Please select a script to run.')

            selected_script = selected_script_item.text()
            script_path = os.path.join(self.scripts_dir, selected_script)

            # Load the selected script module
            self.load_script_module(script_path)

            images = convert_pdf_to_images(self.pdf_file)
            self.current_image = images[0] if images else None

            self._handle_image_comparison()
            self._run_precondition_check(images)
            extracted_data = self._extract_data()  # Store the extracted data

        except ImportError as e:
            raise ImportError(f'Import error: {e}') from e  # Chain the exception

    

    def display_image_with_boxes(self, image, bounding_boxes):
        """Display image with boxes and save box coordinates."""
        self.db_manager.save_bounding_boxes(
            image_id=self.current_image_id,
            boxes=bounding_boxes
        )
        # ...existing drawing code...
        """
        Displays the image with bounding boxes in a new pop-out window.
        
        Args:
            image (PIL.Image.Image): The image to display.
            bounding_boxes (dict): Dictionary of bounding boxes with section names as keys.
        """
        # Draw bounding boxes on the image
        draw = ImageDraw.Draw(image)
        for section, box in bounding_boxes.items():
            x, y, width, height = box
            draw.rectangle([(x, y, x + width, y + height)], outline="red", width=2)
            draw.text((x, y - 15), section, fill="red")  # Label the sections

        # Convert PIL image to QPixmap
        image_qt = self.pil2pixmap(image)

        # Open a new window to display the image
        self.image_window = ImageDisplayWindow(image_qt, self)
        self.image_window.exec_()

    def pil2pixmap(self, pil_image):

        """Convert PIL Image to QPixmap."""
        rgb_image = pil_image.convert('RGB')
        data = rgb_image.tobytes('raw', 'RGB')
        qimage = QImage(data, rgb_image.width, rgb_image.height, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    def extract_text_from_box(self, image, box):
        """Extract text from image box and save to database."""
        text = pytesseract.image_to_string(
            image.crop((box[0], box[1], box[0] + box[2], box[1] + box[3]))
        )
        self.db_manager.save_extracted_text(
            image_id=self.current_image_id,
            section=self.current_section,
            text=text.strip()
        )
        return text.strip()

    def extract_investment_data(self, text):

        """
        Extracts investment experience data from the extracted text.
        
        Args:
            text (str): The extracted text from the PDF.
        
        Returns:
            dict: Extracted investment data.
        """
        patterns = {
            "Investment Experience": r"Investment Experience:\s*(.+)",
            "Years of Experience": r"Years of Experience:\s*(\d+)",
            "Primary Investments": r"Primary Investments:\s*(.+)"
        }
        
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            data[key] = match.group(1).strip() if match else None
        return data

    def extract_client_profile(self, text):

        """
        Extracts client profile data from the extracted text.
        
        Args:
            text (str): The extracted text from the PDF.
        
        Returns:
            dict: Extracted client profile data.
        """
        patterns = {
            "Client Name": r"Client Name:\s*(.+)",
            "Client Age": r"Age:\s*(\d+)",
            "Client Address": r"Address:\s*(.+)"
        }
        
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            data[key] = match.group(1).strip() if match else None
        return data

    def extract_account_profile(self, text):

        """
        Extracts account profile data from the extracted text.
        
        Args:
            text (str): The extracted text from the PDF.
        
        Returns:
            dict: Extracted account profile data.
        """
        patterns = {
            "Account Number": r"Account Number:\s*(\d+)",
            "Account Type": r"Account Type:\s*(.+)"
        }
        
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            data[key] = match.group(1).strip() if match else None
        return data

    def view_extracted_data(self):
        try:
            # Use DatabaseManager to fetch data
            db_manager = DatabaseManager()
            data = db_manager.get_processed_documents()

            if data:
                # Convert the data to a pandas DataFrame
                df = pd.DataFrame(data, columns=[description[0] for description in db_manager.get_cursor().description])
            else:
                QMessageBox.information(self, 'Info', 'No extracted data found in the database.')
                return

            # Create a QTableView to display the DataFrame
            table_view = QTableView()
            model = PandasModel(df) 
            table_view.setModel(model)
            
            # Connect cell click to image display
            table_view.clicked.connect(self.show_image_snippet)  # Connect to your function


            # Adjust column widths to fit content
            header = table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)

            # Create a new window to display the table
            data_window = QWidget()
            data_window.setWindowTitle("Extracted Data Viewer")
            data_window_layout = QVBoxLayout()
            data_window_layout.addWidget(table_view)
            data_window.setLayout(data_window_layout)
            data_window.show()

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while viewing data: {e}')
        finally:
            conn.close()  # Close the database connection

    def show_image_snippet(self, index: QModelIndex):
        """Displays the image snippet corresponding to the clicked cell."""
        # Get data from the clicked cell
        document_name = index.siblingAtColumn(0).data()  # Assuming document name is in the first column
        page_number = index.siblingAtColumn(1).data()  # Assuming page number is in the second column
        field_name = index.siblingAtColumn(2).data()  # Assuming field name is in the third column
        
        try:
            # Connect to the database
            cursor = self.database_manager.get_cursor()

            # Retrieve bounding box and image path
            cursor.execute("SELECT box_x, box_y, box_width, box_height, document_name FROM completed_records WHERE document_name = ? AND page_number = ? AND field_name = ?", (document_name, page_number, field_name))
            result = cursor.fetchone()

            if result:
                x, y, width, height, _ = result
                bounding_box = {"field": (x, y, width, height)}  # Assuming you want to display only one box
                image_path = os.path.join("images", document_name.replace(".pdf", f"_page_{page_number}.png"))  # Construct image path
                
                # Display the image snippet
                self.display_image_with_boxes(Image.open(image_path), bounding_box) 
            else:
                QMessageBox.warning(self, "Warning", "No bounding box information found for this cell.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        except (TypeError, ValueError) as e:
            QMessageBox.warning(self, "Warning", f"Invalid data type retrieved from database: {e}")
        finally:
            self.database_manager.close_connection()

    def move_record_to_completed(self, document_name, page_number, field_name):
        """Moves a record from records_to_be_validated to completed_records."""
        
        try:
            conn = self.database_manager.get_connection()
            cursor = self.database_manager.get_cursor()

            # Get the record from records_to_be_validated
            cursor.execute("SELECT * FROM records_to_be_validated WHERE document_name=? AND page_number=? AND field_name=?", (document_name, page_number, field_name))
            record = cursor.fetchone()

            if record:
                # Insert the record into completed_records
                cursor.execute("INSERT INTO completed_records (document_name, page_number, field_name, field_value, account_number, box_x, box_y, box_width, box_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", record)

                # Delete the record from records_to_be_validated
                cursor.execute("DELETE FROM records_to_be_validated WHERE document_name=? AND page_number=? AND field_name=?", (document_name, page_number, field_name))

                conn.commit()  # Commit changes
                QMessageBox.information(self, "Information", "Record moved to completed records.")
            else:
                QMessageBox.warning(self, "Warning", "Record not found in records_to_be_validated.")

        except sqlite3.Error as e:
            logger.exception(f"Database error moving record: {e}")  # Log the exception
            QMessageBox.critical(self, "Error", f"Database error moving record: {e}")
            if conn:
                conn.rollback()        

    def update_bounding_box_in_db(self, document_name, page_number, field_name, new_x, new_y, new_width, new_height):        
        try:
            conn = self.database_manager.get_connection()
            cursor = self.database_manager.get_cursor()
            
            cursor.execute(
                "UPDATE records_to_be_validated "
                "SET box_x = ?, box_y = ?, box_width = ?, box_height = ? "
                "WHERE document_name = ? AND page_number = ? AND field_name = ?",
                (new_x, new_y, new_width, new_height, document_name, page_number, field_name)
            )
            
            conn.commit()            
            QMessageBox.information(self, "Information", "Bounding box updated successfully.")

            # Move the record to the 'completed_records' table
            self.move_record_to_completed(document_name, page_number, field_name)
            
        except sqlite3.Error as e:
            logger.error(f"Database error updating bounding box: {e}")
            QMessageBox.critical(self, "Error", f"Database error updating bounding box: {e}")
            conn.rollback()  # Rollback changes if an error occurs
            
    def update_record_value(self, document_name, page_number, field_name, new_value):
        """Updates the field_value in the records_to_be_validated table."""
        try:            
            # Use the database_manager to update the record
            self.database_manager.update_record("records_to_be_validated", {"field_value": new_value},
                                                 f"document_name = '{document_name}' AND page_number = {page_number} AND field_name = '{field_name}'")

            logger.info(f"Updated record: {document_name}, Page: {page_number}, Field: {field_name}, New Value: {new_value}")  
        except Exception as e:
            logger.exception(f"Error updating record value: {e}")
            QMessageBox.critical(self, "Error", f"Error updating record value: {e}")            




    def update_document_status(self, document_name, status):
        """Updates the status of a document in the database using DatabaseManager."""
        try:            
            self.database_manager.update_document_status(document_name, status)
            logging.info(f"Updated status of document '{document_name}' to '{status}'")
        except Exception as e:
            logging.error(f"Error updating document status: {e}")
            QMessageBox.critical(self, "Error", f"Error updating document status: {e}")

    def process_backlog_item(self, item, db_manager):
        """Process a single backlog item using centralized handler."""
        return handle_backlog(item, db_manager)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app = SimpleUI()  # Use SimpleUI without any arguments
    app.show()
    sys.exit(app.exec_())

