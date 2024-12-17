# FILE:SIMPLE_UI.PY

import sys
import os
import sqlite3

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

import json
import re
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout, QDialog, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage, QPen, QColor, QFont
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import importlib.util
import subprocess
import time
import logging
import tempfile
import csv
import pandas as pd
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QComboBox
from skimage.metrics import structural_similarity as ssim
from pdf_processor.ui.scripts.extract_utils import extract_data_from_pdf_with_config # new import
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QProgressBar, QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import QRectF

from typing import Any  # new import
from pdf_processor.logic.pdf_processor import (  # Importing from pdf_processor.py
    initialize_database, # new import
    extract_text_with_tesseract, 
    extract_account_number,
    precondition_check, 
    process_pdf_with_config,
    compare_images, 
    show_image_comparison_dialog,
    extract_data_from_pdf,  # New import
    convert_pdf_to_images
    
) 

# Set up logging
logging.basicConfig(filename='pdf_processor.log', level=logging.ERROR, 
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


class BacklogRecord:
    def __init__(self, document_name, page_number, field_name, pdf_path):
        self.document_name = document_name
        self.page_number = page_number
        self.field_name = field_name
        self.pdf_path = pdf_path  # Store the path to the PDF file


class ImageDisplayWindow(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.resize(pixmap.width(), pixmap.height())

        layout = QVBoxLayout()
        scroll = QScrollArea()
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        scroll.setWidget(self.graphics_view)
        layout.addWidget(scroll)

        # Add a button to trigger text extraction
        self.extract_button = QPushButton("Extract Text", self)
        self.extract_button.clicked.connect(self.extract_text_from_selected_area)  # Connect to the extract function
        layout.addWidget(self.extract_button)

        self.setLayout(layout)

        # Add a rectangle for selection
        self.selection_rect = self.scene.addRect(0, 0, 100, 100, QPen(QColor(255, 0, 0)))  # Initial size and color
        self.selection_rect.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # Make it movable
        # Add attributes to store the original position and size of the rectangle
        self.selection_rect.setData(0, self.selection_rect.pos())
        self.selection_rect.setData(1, self.selection_rect.rect().size())

        self.is_dragging = False  # Flag to track dragging state
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        """Handles mouse press events to start dragging."""
        if event.button() == Qt.LeftButton:
            item = self.scene.itemAt(event.scenePos(), self.graphics_view.transform())
            if item == self.selection_rect:
                self.is_dragging = True
                self.drag_start_pos = event.scenePos() - self.selection_rect.scenePos()
                self.selection_rect.setPen(QPen(QColor(0, 255, 0), 2))  # Change color during drag
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handles mouse move events to update the rectangle position during dragging."""
        if self.is_dragging:
            self.selection_rect.setPos(event.scenePos() - self.drag_start_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handles mouse release events to stop dragging and update the database."""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.selection_rect.setPen(QPen(QColor(255, 0, 0)))  # Reset color

            # Update database with new bounding box coordinates (replace with your implementation)
            new_x = int(self.selection_rect.rect().x())
            new_y = int(self.selection_rect.rect().y())
            new_width = int(self.selection_rect.rect().width())
            new_height = int(self.selection_rect.rect().height())
            
            self.parent().update_bounding_box_in_db(new_x, new_y, new_width, new_height)

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def extract_text_from_selected_area(self):
        """Extracts text from the area defined by the selection rectangle."""
        # Get the current position and size of the rectangle
        rect = self.selection_rect.rect()
        x = int(rect.x())
        y = int(rect.y())
        width = int(rect.width())
        height = int(rect.height())

        # Assuming self.parent() is the SimpleUI instance
        if isinstance(self.parent(), SimpleUI):
            # Get the original PIL Image from the parent
            original_image = self.parent().current_image

            if original_image:
                # Call the extract_text_from_box method with the adjusted coordinates
                extracted_text = self.parent().extract_text_from_box(original_image, (x, y, width, height))
                # Do something with the extracted text, like display it
                QMessageBox.information(self, "Extracted Text", extracted_text)
            else:
                QMessageBox.warning(self, "Warning", "No image loaded.")
        else:
            QMessageBox.warning(self, "Warning", "Could not access original image.")

class SimpleUI(QWidget):

    def connect_to_database(self, max_retries=3, retry_delay=1):
        """
        Establishes a connection to the SQLite database with retry mechanism.
        """
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect('extracted_data.db')
                logging.info(f"Database connection successful (attempt {attempt + 1})")
                return conn
            except sqlite3.Error as e:
                logging.warning(f"Database connection failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    QMessageBox.critical(self, "Database Connection Error",
                                        f"Failed to connect to the database after {max_retries} attempts.\n"
                                        "Please check file permissions and verify the database file location.")
                    raise  # Re-raise the exception to stop further execution

    def __init__(self):
        super().__init__()
        # Get the directory containing simple_ui.py
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Add current_image attribute to store the loaded image
        self.current_image = None

        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        self.backlog_queue = []  # Initialize the backlog queue
        
        print(f"Base directory: {self.base_dir}")
        print(f"Scripts directory: {self.scripts_dir}")        
        
        try:
            # Verify scripts directory exists
            if not os.path.exists(self.scripts_dir):
                QMessageBox.warning(self, 'Warning', f'Scripts directory not found at: {self.scripts_dir}')
                return
            
            self.initUI()
        except FileNotFoundError as e:
            QMessageBox.critical(self, 'Error', f'File not found during initialization: {e}')
            logging.exception("File not found during initialization: %s", e)
        except OSError as e:
            QMessageBox.critical(self, 'Error', f'OS error during initialization: {e}')
            logging.exception("OS error during initialization: %s", e)


    def handle_file_io_error(self, error, file_path, operation="read"):
        """Handles file I/O errors with logging and user feedback."""
        error_message = f"Error {operation}ing file '{file_path}': {error}"
        logging.error(error_message)
        QMessageBox.critical(self, "File Error", error_message)

    def read_json_file(self, file_path):
        """Reads a JSON file with error handling."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
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
            logging.exception("Failed to load script module %s: %s", script_path, e)
            raise ImportError(f"Failed to load script module {script_path}: {str(e)}")

    def initUI(self):
        try:
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
                logging.exception("Failed to create configs directory: %s", e)
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
                self.config_combo_box.addItems(self.config_files)
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
            logging.exception("An error occurred during config file loading: %s", e)       

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
        
        # Picklist for config files
        self.picklist_layout = QVBoxLayout()
        self.picklist_label = QLabel("Select Data to Extract:", self)
        self.picklist_label.setFont(QFont("Arial", 12, QFont.Bold))  # Make label bold
        self.picklist_layout.addWidget(self.picklist_label)
        
        self.config_picklists = {}  # Store picklists for each config file
        self.create_config_picklists()
        
        layout.addLayout(self.picklist_layout)

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
            self.progress_bar.setFormat(SC2_MESSAGES[self.progress_message_index])
            self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)
        # If the progress bar is in determinate state (maximum > 0), show progress percentage
        else:
            self.progress_bar.setFormat(f"{self.progress_bar.value()}/{self.progress_bar.maximum()} - {SC2_MESSAGES[self.progress_message_index]}")
            self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)        
        self.progress_bar.setFormat(SC2_MESSAGES[self.progress_message_index])
        self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)

    def handle_duplicate_account_number(self, existing_record, new_record):
        """
        Handles duplicate account numbers by displaying a dialog to the user.

        Args:
            existing_record: The existing record from the database.
            new_record: The new record being imported.
        """
        try:
            # Get image paths for both records
            existing_image_path = os.path.join("images", existing_record[1].replace(".pdf", f"_page_1.png"))  # Assuming document name is in the second column (index 1)
            new_image_path = os.path.join("images", new_record['document_name'].replace(".pdf", f"_page_1.png"))
            
            # Load images with error handling
            existing_image = Image.open(existing_image_path)
            new_image = Image.open(new_image_path)

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Duplicate Account Number Found")
            layout = QGridLayout(dialog)

            # Display images
            layout.addWidget(QLabel("Existing Record:"), 0, 0)
            layout.addWidget(QLabel(QPixmap.fromImage(self.pil2qimage(existing_image))), 1, 0)
            layout.addWidget(QLabel("New Record:"), 0, 1)
            layout.addWidget(QLabel(QPixmap.fromImage(self.pil2qimage(new_image))), 1, 1)

            # Add buttons
            update_button = QPushButton("Update Existing")
            replace_button = QPushButton("Replace Existing")
            skip_button = QPushButton("Skip New")
            layout.addWidget(update_button, 2, 0)
            layout.addWidget(replace_button, 2, 1)
            layout.addWidget(skip_button, 3, 0, 1, 2)  # Span across two columns

            # Connect buttons to actions
            update_button.clicked.connect(lambda: self.resolve_duplicate(dialog, "update", existing_record, new_record))
            replace_button.clicked.connect(lambda: self.resolve_duplicate(dialog, "replace", existing_record, new_record))
            skip_button.clicked.connect(lambda: self.resolve_duplicate(dialog, "skip", existing_record, new_record))

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error handling duplicate account number: {e}")
            logging.exception("Error handling duplicate account number: %s", e)

    def pil2qimage(self, pil_image):
        """Convert PIL Image to QImage."""
        rgb_image = pil_image.convert('RGB')
        data = rgb_image.tobytes('raw', 'RGB')
        return QImage(data, rgb_image.width, rgb_image.height, QImage.Format_RGB888)

    def resolve_duplicate(self, dialog, action, existing_record, new_record):
        """Resolves the duplicate account number based on user's choice."""
        dialog.close()
        if action == "update":
            # ... (Logic to update existing record with new data) ...
            pass
        elif action == "replace":
            # ... (Logic to replace existing record with new record) ...
            pass
        elif action == "skip":
            logging.info(f"Skipped record with account number {new_record['account_number']} from {new_record['document_name']}")

    def add_records_to_db(self):
        """ 
        Populates the 'extracted_data' database table with information
        from the JSON config files (excluding 'all_data_config.json').

        # Database connection
        conn = sqlite3.connect('extracted_data.db')
        cursor = conn.cursor()
        Populates the 'extracted_data' database table with information
        from the JSON config files (excluding 'all_data_config.json').
        """
        try:
            
            # Database connection
            conn = self.connect_to_database()
            cursor = conn.cursor()        
            
            # Initialize tables if they don't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS completed_records ( ... )''') # define schema
            cursor.execute('''CREATE TABLE IF NOT EXISTS records_to_be_validated ( ... )''') # define schema
            cursor.execute('''CREATE TABLE IF NOT EXISTS incomplete_records ( ... )''') # define schema

            if not self.input_directory or not self.output_directory:
                QMessageBox.warning(self, 'Warning', 'Please select input and output directories.')
                return

            QMessageBox.information(self, "Information", "This operation may take a while. Please be patient.")
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(len(self.config_files) -1 )  # Exclude all_data_config.json
            self.progress_bar.setValue(0)
            self.progress_timer.start(1000)  # Update message every 1000ms (1 second)
            self.show_message("Starting database population...")  # Display a message
            null_value_records = []  # Initialize the list to store records with null values

            config_index = 0  # Initialize config file index for progress bar
            try:                
                for config_file in self.config_files:
                    if config_file != "all_data_config.json":  # Exclude all_data_config
                        config_path = os.path.join(self.config_dir, config_file)
                        
                        # Process each PDF in the input directory
                        for filename in os.listdir(self.input_directory):
                            if filename.endswith(".pdf"):
                                pdf_path = os.path.join(self.input_directory, filename)
                                
                                # Extract data from the PDF using the current config file
                                extracted_data = extract_data_from_pdf_with_config(pdf_path, config_path)

                                # Iterate through extracted data and insert non-null records into the database
                                for page_number, page_data in extracted_data.items():                                    
                                    for field_name, field_value in page_data.items():
                                        if field_value is not None:  # Only insert if field value is not null
                                            try:
                                                # Check for duplicate account number
                                                account_number = extracted_data.get(1, {}).get('Account Number')  # Assuming account number is on page 1
                                                if account_number:
                                                    cursor.execute("SELECT * FROM completed_records WHERE account_number = ?", (account_number,))
                                                    existing_record = cursor.fetchone()                                                    
                                                    if existing_record:
                                                        self.handle_duplicate_account_number(existing_record, {'document_name': os.path.basename(pdf_path), **page_data})
                                                        break  # Skip to the next PDF if duplicate is handled

                                                # Insert into completed_records                                                    
                                                cursor.execute(
                                                    "INSERT INTO completed_records (document_name, page_number, field_name, field_value, account_number, box_x, box_y, box_width, box_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                                    (os.path.basename(pdf_path), page_number, field_name, field_value, account_number,
                                                     page_data.get(field_name + '_bbox', [None])[0],  # x
                                                     page_data.get(field_name + '_bbox', [None, None])[1],  # y
                                                     page_data.get(field_name + '_bbox', [None, None, None])[2],  # width
                                                     page_data.get(field_name + '_bbox', [None, None, None, None])[3])  # height
                                                )                                                                                                
                                                
                                        else:
                                            # Insert into incomplete_records
                                            cursor.execute(
                                                "INSERT INTO incomplete_records (document_name, page_number, field_name) VALUES (?, ?, ?)",
                                                (os.path.basename(pdf_path), page_number, field_name)
                                            )
                                            self.backlog_queue.append(BacklogRecord(os.path.basename(pdf_path), page_number, field_name, pdf_path))
                                            
                        config_index += 1  # Increment config file index
                        self.progress_bar.setValue(config_index)  # Update progress bar
                        self.update_progress_message()  # Update progress message
                # Move the conn.commit() statement after processing all PDFs
                conn.commit() 

                                                # ... (Existing insertion code) ...
                                            except sqlite3.IntegrityError as e:
                                                # ... (Existing IntegrityError handling) ...
                                                cursor.execute(
                                                    "INSERT INTO completed_records (document_name, page_number, field_name, field_value, account_number, box_x, box_y, box_width, box_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                                    (os.path.basename(pdf_path), page_number, field_name, field_value, account_number,
                                                     page_data.get(field_name + '_bbox', [None])[0],  # x
                                                     page_data.get(field_name + '_bbox', [None, None])[1],  # y
                                                     page_data.get(field_name + '_bbox', [None, None, None])[2],  # width
                                                     page_data.get(field_name + '_bbox', [None, None, None, None])[3])  # height
                                                )
                                            except Exception as e:
                                                logging.exception("Error during database operation: %s", e)
                                                QMessageBox.critical(self, 'Error', f'An error occurred during database operation: {e}')
                                                conn.rollback()  # Rollback changes if an error occurs
                                                
                                        else:
                                            # Insert into incomplete_records
                                            cursor.execute(
                                                "INSERT INTO incomplete_records (document_name, page_number, field_name) VALUES (?, ?, ?)",
                                                (os.path.basename(pdf_path), page_number, field_name)
                                            )
                                            self.backlog_queue.append(BacklogRecord(os.path.basename(pdf_path), page_number, field_name, pdf_path))

                    config_index += 1  # Increment config file index
                    self.progress_bar.setValue(config_index)  # Update progress bar
                    self.update_progress_message()  # Update progress message


        # Report null values if any
        if self.backlog_queue:
            QMessageBox.information(self, "Information: Null Values Detected", "Some records were skipped due to null values. Please review the backlog queue.")
            self.update_backlog_list()  # Update the backlog list widget

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, 'Error', f'An error occurred during database population: {e}')
            logging.exception("Error during database population: %s", e)
        finally:
            conn.close()
            cursor.close() 

        self.progress_timer.stop()  # Stop the progress bar timer
        self.progress_bar.reset()  # Reset the progress bar
        self.show_message("Database population completed!")  # Display a completion message

        # Report null values if any
        if self.backlog_queue:
            QMessageBox.information(self, "Information: Null Values Detected", "Some records were skipped due to null values. Please review the backlog queue.")
            self.update_backlog_list()  # Update the backlog list widget

    def show_message(self, message):
        self.progress_bar.setFormat(SC2_MESSAGES[self.progress_message_index] + " - " + message)
        self.progress_message_index = (self.progress_message_index + 1) % len(SC2_MESSAGES)

    def start_progress(self):
        try:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_timer.start(1000)  # Update message every 1000ms (1 second)
            """Displays a message to the user (replace with your preferred method)."""
            print(message)  # Or use QMessageBox, logging, etc.

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error displaying page: {e}")
            logging.exception(f"Error displaying page: {e}")
            return

    def create_config_picklists(self):
        try:
            for config_file in self.config_files:
                if config_file != "all_data_config.json":  # Exclude all_data_config
                    config_path = os.path.join(self.config_dir, config_file)
                    with open(config_path, 'r') as f:
                        config_data = self.read_json_file(config_path) # Use read_json_file with error handling
                    
                    picklist = QListWidget(self)
                    picklist.addItems(config_data.keys())  # Add field names to picklist
                    
                    config_name = config_file.replace("_config.json", "").replace("_", " ").title()  # User-friendly name
                    self.picklist_layout.addWidget(QLabel(config_name, self))
                    self.picklist_layout.addWidget(picklist)
                    self.config_picklists[config_file] = picklist  # Store the picklist
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error displaying page: {e}")
            logging.exception(f"Error displaying page: {e}")
            return

    def display_dataframe_head(self, df):

        """Prints the first 5 rows of the DataFrame to the console."""
        print("DataFrame Head:")
        print(df.head())

    def validate_and_convert_data_types(self, data_dict: dict[str, Any]) -> dict[str, Any]:
        """Validates and converts data types to match the database schema."""
        validated_data = {}
        for field_name, field_value in data_dict.items():
            expected_type = DATABASE_SCHEMA.get(field_name)
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
                QMessageBox.warning(self, 'Warning', f'Scripts directory not found: {self.scripts_dir}')
                logging.warning("Scripts directory not found: %s", self.scripts_dir)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading scripts: {e}')
            logging.exception("Error loading scripts: %s", e)

    def select_input_directory(self):

        directory = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if directory:
            self.input_directory = directory
            self.input_dir_path.setText(directory)

    def select_output_directory(self):

        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.output_directory = directory
            self.output_dir_path.setText(directory)

    def extract_to_files(self):
        """
        Performs file-based extraction.
        """
        if not self.input_directory or not self.output_directory:
            QMessageBox.warning(self, 'Warning', 'Please select input and output directories.')
            return

        for filename in os.listdir(self.input_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.input_directory, filename)
                output_file = os.path.join(self.output_directory, filename[:-4] + ".txt")  # Example output file name

                try:
                    # ... (Your existing logic to extract data and write to file) ...
                    # Example with error handling:
                    extracted_data = extract_data_from_pdf(pdf_path, self.config_file) 
                    with open(output_file, 'w') as f:
                        json.dump(extracted_data, f, indent=4)

                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Error processing {filename}: {e}')
                    logging.exception(f"Error processing {filename}: %s", e)

        QMessageBox.information(self, 'Information', 'File-based extraction completed.')

    def process_pdf(self):

        def compare_images(image1, image2, threshold=0.95):
            """Compares two images using SSIM and returns True if they are similar."""
            image1 = image1.convert("L")  # Convert to grayscale
            image2 = image2.convert("L")
            ssim_score = ssim(image1, image2)
            return ssim_score >= threshold
        
        def show_image_comparison_dialog(image1, image2):

            """Displays a dialog showing both images for user comparison."""
            dialog = QDialog(self) # Assuming QDialog is imported
            dialog.setWindowTitle("Image Comparison") 
            layout = QHBoxLayout() 

            # Convert PIL Images to QPixmap and add them to the layout
            pixmap1 = self.pil2pixmap(image1) 
            pixmap2 = self.pil2pixmap(image2)
            label1 = QLabel() # Assuming QLabel is imported
            label1.setPixmap(pixmap1)
            label2 = QLabel()
            label2.setPixmap(pixmap2)
            layout.addWidget(label1)
            layout.addWidget(label2)
            dialog.setLayout(layout)

            # Add buttons for user confirmation
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) # Assuming QDialogButtonBox is imported
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show the dialog and return the result
            result = dialog.exec_()
            return result == QDialog.Accepted  # True if OK is pressed, False otherwise

        if not self.input_directory or not self.output_directory or not self.pdf_file or not self.config_file:
            QMessageBox.warning(
                self,
                'Warning',
                'Please select input directory, output directory, PDF file, and config file.'
            )
            return

        selected_script_item = self.script_list.currentItem()

        # Determine extraction type
        if self.file_based_radio.isChecked():
            self.extract_to_files()
            return
        # Otherwise, proceed with database-based extraction as before

        if not selected_script_item:
            QMessageBox.warning(self, 'Warning', 'Please select a script to run.')
            return

        selected_script = selected_script_item.text()
        script_path = os.path.join(self.scripts_dir, selected_script)

        try:
            # Load the selected script module
            script_module = self.load_script_module(script_path)
            print(f"Loaded script: {selected_script}")

            # Call the main function of the script module, passing input and output directories
            # if hasattr(script_module, 'main'):
            #     self.run_script_with_config(script_path)
            # else:
            #     QMessageBox.warning(self, 'Warning', f"The selected script '{selected_script}' does not have a 'main' function.")
            #     return
            
            # Convert PDF to images for precondition checking
            
            images = convert_pdf_to_images(self.pdf_file) # moved to pdf_processor.py
            self.current_image = images[0] if images else None  # Store the first image, handle empty list

            # Image comparison before extraction
            if self.previous_image_path:
                    try:
                        previous_image = Image.open(self.previous_image_path)
                        if not compare_images(self.current_image, previous_image):
                            if not show_image_comparison_dialog(self.current_image, previous_image):
                                QMessageBox.information(self, "Information", "Extraction cancelled.")
                                return  # Stop the process if the user cancels
                    except FileNotFoundError:
                        QMessageBox.warning(self, "Warning", "Previous image file not found.")
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Error comparing images: {e}")

            # Store current image for next comparison
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                try:
                    self.current_image.save(temp_file.name)
                except AttributeError as e:  # Handle case where current_image is None
                    logging.warning(f"Could not save current image: {e}")
                self.previous_image_path = temp_file.name

            # Run the precondition checker before processing
            precondition_results = precondition_check(images)
            self.display_dataframe_head(pd.DataFrame(precondition_results))            
            extracted_data = extract_data_from_pdf(self.pdf_file, self.config_file)
            print(extracted_data)            

            # If all_data_config.json is selected, show progress bar
            if self.config_file.endswith("all_data_config.json"):
                QMessageBox.warning(self, "Warning", "This operation may take a while. Please be patient.")
                self.start_progress()  # Start progress bar with rotating messages
                
                # ... your long-running database import operation here ...
                
                self.progress_timer.stop()  # Stop the progress bar timer
                self.progress_bar.reset()  # Reset the progress bar
                QMessageBox.information(self, "Information", "Database import completed!")

            #account_number = precondition_results.get("Account Number", "Not Found")
            #account_name = precondition_results.get("Account Name", "Not Found")            
        except ImportError as e:
            QMessageBox.critical(self, 'Error', f'Import error: {e}')
            logging.exception("Import error: %s", e)

    def display_image_with_boxes(self, image, bounding_boxes):
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
            draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=2)
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

        """
        Crops the image to the bounding box and extracts text using OCR.
        
        Args:
            image (PIL.Image.Image): The original image.
            box (tuple): Bounding box coordinates (x, y, width, height).
        
        Returns:
            str: Extracted text.
        """
        x, y, width, height = box
        cropped_img = image.crop((x, y, x + width, y + height))
        text = pytesseract.image_to_string(cropped_img)
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
            # Connect to the database
            conn = self.connect_to_database()  # Use the connection function with retry
            cursor = conn.cursor()

            # Fetch all data from the extracted_data table
            cursor.execute("SELECT * FROM completed_records")  # Changed to completed_records
            data = cursor.fetchall()

            # Convert the data to a pandas DataFrame
            df = pd.DataFrame(data, columns=[description[0] for description in cursor.description])

            # Create a QTableView to display the DataFrame
            table_view = QTableView()
            model = PandasModel(df)  # Assuming PandasModel is defined (see below)
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
            logging.exception("Error viewing extracted data: %s", e)
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
            conn = self.connect_to_database()  # Use the connection function with retry
            cursor = conn.cursor()

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
            conn.close()

    def move_record_to_completed(self, document_name, page_number, field_name):
        """Moves a record from records_to_be_validated to completed_records."""
        try:
            conn = self.connect_to_database()  # Use the connection function with retry
            cursor = conn.cursor()

            # Get the record from records_to_be_validated
            cursor.execute("SELECT * FROM records_to_be_validated WHERE document_name = ? AND page_number = ? AND field_name = ?", (document_name, page_number, field_name))
            record = cursor.fetchone()

            if record:
                # Insert the record into completed_records
                cursor.execute("INSERT INTO completed_records (document_name, page_number, field_name, field_value, account_number, box_x, box_y, box_width, box_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", record[1:])  # Exclude the primary key from records_to_be_validated

                # Delete the record from records_to_be_validated
                cursor.execute("DELETE FROM records_to_be_validated WHERE document_name = ? AND page_number = ? AND field_name = ?", (document_name, page_number, field_name))

                conn.commit()
                QMessageBox.information(self, "Information", "Record moved to completed records.")

                # Update the UI (remove the record from the records_to_be_validated display)
                # ... (Implementation to remove the record from the UI) ...

            else:
                QMessageBox.warning(self, "Warning", "Record not found in records_to_be_validated.")

        except sqlite3.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        finally:
            conn.close()

    def update_bounding_box_in_db(self, new_x, new_y, new_width, new_height):
        """Updates the bounding box coordinates in the database."""
        try:
            # Get the document name, page number, and field name from the current selection
            # (You'll need to implement this based on how your selection is tracked)
            # For example:
            # document_name = self.current_selection['document_name']
            # page_number = self.current_selection['page_number']
            # field_name = self.current_selection['field_name']

            # Connect to the database
            conn = self.connect_to_database()  # Use the connection function with retry
            cursor = conn.cursor()

            # Update the bounding box coordinates in the database
            cursor.execute(
                "UPDATE records_to_be_validated SET box_x = ?, box_y = ?, box_width = ?, box_height = ? WHERE document_name = ? AND page_number = ? AND field_name = ?",
                (new_x, new_y, new_width, new_height, document_name, page_number, field_name)  # Replace with actual values
            )
            conn.commit()

            QMessageBox.information(self, "Information", "Bounding box coordinates updated successfully.")

            # Move the record to completed_records after successful update
            self.move_record_to_completed(document_name, page_number, field_name) 

            # Refresh the image snippet (optional)
            # self.show_image_snippet()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        finally:
            conn.close()

    def update_backlog_list(self):
        """Updates the backlog list widget with items from the backlog queue."""
        self.backlog_list.clear()
        for record in self.backlog_queue:
            item_text = f"{record.document_name} - Page {record.page_number} - Field: {record.field_name}"
            self.backlog_list.addItem(item_text)

    def review_backlog(self):
        """Handles the 'Review Backlog' button click."""
        if not self.backlog_queue:
            QMessageBox.information(self, "Information", "Backlog queue is empty.")
            return

        selected_item = self.backlog_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a record from the backlog queue.")
            return

        # Get the BacklogRecord object associated with the selected item
        selected_record_index = self.backlog_list.currentRow()
        selected_record = self.backlog_queue[selected_record_index]

        # ... (Logic to display the PDF page, highlight the field, and allow correction) ...
        # Example:
        # Display the PDF page using your existing image display logic
        # Highlight the bounding box of the problematic field
        # Provide a way for the user to enter the correct value (e.g., a text input field)

        # Here's a placeholder for how you might display and highlight the page:
        try:
            images = convert_pdf_to_images(selected_record.pdf_path)  # Assuming your function to convert PDF to images
            page_image = images[selected_record.page_number - 1]  # Adjust for zero-based indexing
            
            # Create a dictionary with the bounding box information of the selected field to display
            try:
                config_file = os.path.join(self.config_dir, self.config_files[0])
            except IndexError:
                config_file = None  # Handle case where no config files are found
            extracted_data = extract_data_from_pdf(selected_record.pdf_path, config_file)
            
            bounding_box = {selected_record.field_name: extracted_data[selected_record.page_number][selected_record.field_name + '_bbox']}
            
            self.display_image_with_boxes(page_image, bounding_box)

        except Exception as e:
            print(f"Error displaying page: {e}")
            QMessageBox.critical(self, "Error", f"Error displaying page: {e}")
            return


        # ... (Logic to update the database with the corrected value) ...
        # After correction, remove the record from the backlog:
        # self.backlog_queue.pop(selected_record_index)
        # self.update_backlog_list()

        QMessageBox.information(self, "Information", "Backlog review functionality is under development.")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleUI()
    ex.show()
    sys.exit(app.exec_())

conn = SimpleUI().connect_to_database()  # Use the connection function with retry
cursor = conn.cursor()

# Create the table with Account Number as primary key and File Name as secondary key
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS extracted_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name TEXT,
    page_number INTEGER,  # Add page number column
    field_name TEXT,    
    field_value TEXT,    
    account_number TEXT,
    box_x INTEGER,  # Add bounding box coordinates
    box_y INTEGER,
    box_width INTEGER,
    box_height INTEGER,
    UNIQUE (account_number, document_name)  # Account Number as primary, File Name as secondary
)
''')
conn.commit()




# Define a PandasModel to display the DataFrame in QTableView
class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None