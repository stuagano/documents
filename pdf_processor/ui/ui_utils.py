import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import messagebox
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QProgressBar, QFileDialog, QComboBox, 
                          QTableView)
from PyQt6.QtCore import Qt, QModelIndex
from PIL import Image, ImageTk


import os
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import logging

CONFIG_DIR = "pdf_processor/ui/scripts/configs"

def load_config_options(configs_dir):
    """Gets the config files from the configs directory and returns a list of strings."""
    config_options = [f for f in os.listdir(configs_dir) if f.endswith(".json")]
    if not config_options:
        QMessageBox.warning(None, "Error", f"No config files found in the '{configs_dir}' directory.")
        return []
    return config_options

def select_input_directory(parent):
    dir_path = QFileDialog.getExistingDirectory(parent, "Select Input Directory")
    return dir_path

def select_output_directory(parent):
    dir_path = QFileDialog.getExistingDirectory(parent, "Select Output Directory")
    return dir_path


def process_pdfs(input_dir, output_dir, config_file, progress_bar):
    if not input_dir or not output_dir:
        return

    try:
        config_path = Path(config_file)
        progress_bar.setRange(0, 0)  # Indeterminate progress
        logging.info(f"Processing PDFs in {input_dir} with config {config_path} to {output_dir}")
        # Placeholder for actual processing logic
        # ...

    except Exception as e:
        logging.error(f"Error processing PDFs: {e}")
        QMessageBox.critical(None, "Error", f"Error processing PDFs: {e}")

    finally:
        progress_bar.setRange(0, 1)
        progress_bar.setValue(1)



# Create the ui_utils.py file if it doesn't exist.
ui_utils_path = "pdf_processor/ui/ui_utils.py"
if not os.path.exists(ui_utils_path):
    with open(ui_utils_path, "w") as f:
        f.write("")  # Create an empty file


# Read the contents of simple_ui.py
simple_ui_path = "pdf_processor/ui/simple_ui.py"
try:
    with open(simple_ui_path, "r") as f:
        simple_ui_content = f.read()
except FileNotFoundError:
    print(f"Error: File '{simple_ui_path}' not found.")
    simple_ui_content = ""

# Regular expression to identify functions (simplified, might need adjustment)
import re
function_pattern = r"def\s+(\w+)\s*\(.*?\):"

# Find all functions in simple_ui.py
functions = re.findall(function_pattern, simple_ui_content)


# Move function definitions to ui_utils.py
with open(ui_utils_path, "a") as ui_utils_file:
  for function in functions:
    # Find function definition and its body.
    function_definition = re.search(rf"def\s+{function}\s*\(.*?\):(.*?)(?=\n\s*def|$)", simple_ui_content, re.DOTALL)
    if function_definition:
      ui_utils_file.write(function_definition.group(0) + "\n")
    
    #Replace function in simple_ui with import.
    simple_ui_content = re.sub(rf"def\s+{function}\s*\(.*?\):(.*?)(?=\n\s*def|$)", "", simple_ui_content, flags = re.DOTALL)


#Update simple_ui.py to import moved functions
with open(simple_ui_path, "w") as f:
    f.write("from .ui_utils import *\n\n") #Import all functions from ui_utils
    f.write(simple_ui_content)


def load_config_options(configs_dir):
    """Gets the config files from the configs directory and returns a list of strings."""
    config_options = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    if not config_options:
        messagebox.showerror("Error", f"No config files found in the '{CONFIG_DIR}' directory.")
        return [] 
    return config_options


def load_config_options(configs_dir):
    """Gets the config files from the configs directory and returns a list of strings."""
    config_options = [f for f in os.listdir(configs_dir) if f.endswith(".json")]
    if not config_options:
        messagebox.showerror("Error", "No config files found in the 'configs' directory.")
        return []  # Return an empty list if no config files are found
    return config_options


def create_config_picklists(self):
    """Creates the config file picklists."""
    config_options = load_config_options(
        os.path.join(os.path.dirname(__file__), "scripts", "configs")
    )
    if not config_options:  # If no config files were found, exit the function
        return

    self.config_var.set(config_options[0])  # Set the first option as default

    self.config_dropdown = tk.OptionMenu(self.root, self.config_var, *config_options)
    self.config_dropdown.grid(row=0, column=1, padx=5, pady=5)

    self.output_dir_var.set(self.default_output_dir)  # Setting default output directory


def create_config_picklists_ui(self):
    """Creates the config file picklists."""
    self.config_var = tk.StringVar(self.root)
    self.config_var.set("Select Config")  # Default value

    config_options = [f for f in os.listdir(self.configs_dir) if f.endswith(".json")]
    self.config_dropdown = tk.OptionMenu(self.root, self.config_var, *config_options)
    self.config_dropdown.grid(row=0, column=1, padx=5, pady=5)

    self.output_dir_var = tk.StringVar(self.root)
    self.output_dir_var.set(self.default_output_dir)

    output_dir_label = tk.Label(self.root, text="Output Directory:")
    output_dir_label.grid(row=1, column=0, padx=5, pady=5)

    output_dir_entry = tk.Entry(self.root, textvariable=self.output_dir_var, width=40)
    output_dir_entry.grid(row=1, column=1, padx=5, pady=5)


def _compare_images(image1_path, image2_path):
    """Compares two images and returns True if they are similar, False otherwise."""
    try:
        # Open images using Pillow
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Ensure images are in the same mode (e.g., RGB)
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")

        # Compare images
        return img1.tobytes() == img2.tobytes()

    except FileNotFoundError:
        print(f"Error: One or both image files not found: {image1_path}, {image2_path}")
        return False
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False


def _show_image_comparison_dialog(self, image1_path, image2_path):
    """Shows a dialog with the two images for comparison."""
    comparison_window = tk.Toplevel(self.root)
    comparison_window.title("Image Comparison")

    # Load and resize images
    try:
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Resize images to fit the window
        max_width = 600
        max_height = 400
        img1.thumbnail((max_width, max_height))
        img2.thumbnail((max_width, max_height))

        # Convert images to Tkinter PhotoImage objects
        photo1 = ImageTk.PhotoImage(img1)
        photo2 = ImageTk.PhotoImage(img2)

        # Create labels to display images
        label1 = tk.Label(comparison_window, image=photo1)
        label1.image = photo1  # Keep a reference to avoid garbage collection
        label1.grid(row=0, column=0, padx=10, pady=10)

        label2 = tk.Label(comparison_window, image=photo2)
        label2.image = photo2
        label2.grid(row=0, column=1, padx=10, pady=10)

    except FileNotFoundError:
        messagebox.showerror("Error", "One or both image files not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    # Center the comparison window
    comparison_window.update_idletasks()  # Update window size
    width = comparison_window.winfo_width()
    height = comparison_window.winfo_height()
    x = (comparison_window.winfo_screenwidth() // 2) - (width // 2)
    y = (comparison_window.winfo_screenheight() // 2) - (height // 2)
    comparison_window.geometry(f"+{x}+{y}")


def load_pdf(pdf_path):
    """Loads a PDF file and returns a PyMuPDF Document object."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        return doc
    except ImportError:
        messagebox.showerror(
            "Error",
            "PyMuPDF is not installed. Please install it using 'pip install pymupdf'."
        )
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the PDF: {e}")
        return None


def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def extract_data_from_pdf_with_config(pdf_path, config_path):
    """Extracts data from a PDF file using the specified config file."""
    try:
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

        extracted_data = process_documents.extract_data_from_pdf(pdf_path, config_data)

        return extracted_data

    except FileNotFoundError:
        messagebox.showerror("Error", f"Config file not found: {config_path}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"Invalid JSON in config file: {config_path}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during data extraction: {e}")
        return None

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def load_and_display_pdf(self, pdf_path):
    """Loads and displays the PDF in the canvas."""
    doc = load_pdf(pdf_path)
    if doc is None:
        return  # Exit if PDF loading failed

    self.doc = doc  # Store the document object
    self.current_page = 0

    self.display_page(self.current_page)

    # Update page label
    self.page_label.config(text=f"Page {self.current_page + 1} of {len(self.doc)}")

    # Enable/disable navigation buttons
    self.prev_button.config(state="disabled" if self.current_page == 0 else "normal")
    self.next_button.config(
        state="disabled" if self.current_page == len(self.doc) - 1 else "normal"
    )


def display_page(self, page_num):
    """Displays the specified page of the PDF in the canvas."""
    page = self.doc[page_num]
    zoom = 1.5  # Adjust zoom as needed
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # Convert pixmap to Tkinter-compatible image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    self.photo = ImageTk.PhotoImage(image=img)  # Keep a reference!

    # Clear canvas and display image
    self.canvas.delete("all")
    self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    # Update canvas scroll region
    self.canvas.config(scrollregion=self.canvas.bbox("all"))


def _on_mousewheel(self, event):
    """Handles mousewheel scrolling for the canvas."""
    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def process_pdf(self):
    """Processes the selected PDF file with the chosen config."""
    pdf_path = self.pdf_path_var.get()
    config_name = self.config_var.get()
    output_dir = self.output_dir_var.get()

    if not pdf_path or not config_name or not output_dir:
        messagebox.showerror("Error", "Please select a PDF file, config file, and output directory.")
        return

    config_path = os.path.join(self.configs_dir, config_name)

    try:
        extracted_data = extract_data_from_pdf_with_config(pdf_path, config_path)

        if extracted_data:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Generate output file path
            pdf_filename = os.path.basename(pdf_path)
            output_filename = os.path.splitext(pdf_filename)[0] + "_extracted_data.json"
            output_path = os.path.join(output_dir, output_filename)

            # Save extracted data to JSON file
            with open(output_path, "w") as output_file:
                json.dump(extracted_data, output_file, indent=4)

            messagebox.showinfo("Success", f"Data extracted and saved to: {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing: {e}")

def process_pdf(self):
    """Processes the selected PDF file with the chosen config."""
    pdf_path = self.pdf_path_var.get()
    config_name = self.config_var.get()
    output_dir = self.output_dir_var.get()
    # Additional logic for processing the PDF with the selected configuration
    # ...

def __init__(self, document_name, page_number, field_name, pdf_path):
        self.document_name = document_name
        self.page_number = page_number
        self.field_name = field_name
        self.pdf_path = pdf_path  # Store the path to the PDF file


class SimpleUI(QWidget):
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

def __init__(self, document_name, page_number, field_name, pdf_path):
        self.document_name = document_name
        self.page_number = page_number
        self.field_name = field_name
        self.pdf_path = pdf_path  # Store the path to the PDF file


class SimpleUI(QWidget):
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
    def add_records_to_db(self):
        """Creates database tables if they don't exist, using the provided schema."""
        try:
            self.database_manager.create_tables()  # Use DatabaseManager to create tables
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.exception("Error creating database tables: %s", e)
            QMessageBox.critical(self, 'Error', f'An error occurred during table creation: {e}')
    def _extract_data_from_pdfs(self, config_path):
        """Extracts data from PDFs using a given config file."""
        extracted_data = {}
        for filename in os.listdir(self.input_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.input_directory, filename)
                extracted_data[pdf_path] = extract_data_from_pdf_with_config(pdf_path, config_path)
        return extracted_data
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
    def _add_record_to_backlog(self, pdf_path, page_number, field_name):
        """Adds a record to the backlog queue."""
        self.backlog_queue.append(BacklogRecord(os.path.basename(pdf_path), page_number, field_name, pdf_path))


    
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

                    extracted_data = self._extract_data_from_pdfs(config_path)

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
                                        self.backlog_manager.add_to_backlog(pdf_path, page_number, field_name)                                       
                                else:
                                    self.backlog_manager.add_to_backlog(pdf_path, page_number, field_name)
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

            # ... (Further processing of extracted_data if needed) ...

        except ImportError as e:
            raise ImportError(f'Import error: {e}') from e  # Chain the exception
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
        finally:
            if cursor:
                cursor.close()            
            self.database_manager.close_connection()
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
        finally:            
            self.database_manager.close_connection()    
    def _update_backlog_list(self):
        """Refreshes the backlog list widget with the current backlog items."""
        self.backlog_list.clear()  # Clear existing items
        for record in self.backlog_manager.get_backlog():
            item_text = f"{record.document_name} - Page {record.page_number} - {record.field_name}"
            self.backlog_list.addItem(item_text)  # Add each backlog item to the list widget
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
    def review_backlog(self):
        """Handles the 'Review Backlog' button click."""
        try:            
            self.backlog_manager.review_backlog()
            self._update_backlog_list()  # Update the backlog list widget
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while reviewing the backlog: {e}")
            logging.exception(f"Error reviewing backlog: {e}")  
    def update_document_status(self, document_name, status):
        """Updates the status of a document in the database using DatabaseManager."""
        try:            
            self.database_manager.update_document_status(document_name, status)
            logging.info(f"Updated status of document '{document_name}' to '{status}'")
        except Exception as e:
            logging.error(f"Error updating document status: {e}")
            QMessageBox.critical(self, "Error", f"Error updating document status: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app = SimpleUI()  # Use SimpleUI without any arguments
    app.show()
    sys.exit(app.exec_())
def __init__(self):
        super().__init__()
        self.input_dir = ""
        self.output_dir = ""
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            config_file = self.config_combo.currentText()
            config_path = Path(__file__).parent / 'scripts' / 'configs' / config_file
            
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.input_dir = ""
        self.output_dir = ""
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            config_file = self.config_combo.currentText()
            config_path = Path(__file__).parent / 'scripts' / 'configs' / config_file
            
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        self.input_dir = ""
        self.output_dir = ""
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            config_file = self.config_combo.currentText()
            config_path = Path(__file__).parent / 'scripts' / 'configs' / config_file
            
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            config_file = self.config_combo.currentText()
            config_path = Path(__file__).parent / 'scripts' / 'configs' / config_file
            
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            config_file = self.config_combo.currentText()
            config_path = Path(__file__).parent / 'scripts' / 'configs' / config_file
            
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        from pathlib import Path
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            from pathlib import Path
            config_path = Path(__file__).parent / 'scripts' / 'configs' / self.config_file
            print(f"Processing with config: {config_path}")
            config_path = Path(__file__).parent / 'scripts' / 'configs' / self.config_file
            
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()
        
        # Input directory selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select Input Directory')
        self.input_btn.clicked.connect(self.select_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_btn)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select Output Directory')
        self.output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_btn)
        
        # Config selection
        config_layout = QHBoxLayout()
        self.config_label = QLabel('Config File:')
        self.config_combo = QComboBox()
        self.load_configs()
        config_layout.addWidget(self.config_label)
        config_layout.addWidget(self.config_combo)
        
        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        
        # Add all layouts
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(config_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
        self.setGeometry(100, 100, 600, 200)
def select_input_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_label.setText(f'Input: {dir_path}')
def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f'Output: {dir_path}')
def load_configs(self):
        from pathlib import Path
        config_dir = Path(__file__).parent / 'scripts' / 'configs'
        configs = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        self.config_combo.addItems(configs)
def process_pdfs(self):
        if not self.input_dir or not self.output_dir:
            return
        
        try:
            from pathlib import Path
            config_path = Path(__file__).parent / 'scripts' / 'configs' / self.config_file
            print(f"Processing with config: {config_path}")
            config_path = Path(__file__).parent / 'scripts' / 'configs' / self.config_file
            
            # Process implementation here
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {e}")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""  # Initialize config_file
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select')
        self.input_btn.clicked.connect(self.select_input_directory)  # Connect to ui_utils function
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_btn)

        # Output directory
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select')
        self.output_btn.clicked.connect(self.select_output_directory) # Connect to ui_utils function
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_btn)

        # Config selection
        self.config_combo = QComboBox()
        self.load_configs()
        layout.addWidget(QLabel('Config File:'))
        layout.addWidget(self.config_combo)

        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)  # Connect to ui_utils function
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
def select_input_directory(self):
        self.input_dir = select_input_directory(self) # Call the function from ui_utils
        if self.input_dir:
            self.input_label.setText(f'Input: {self.input_dir}')
def select_output_directory(self):
        self.output_dir = select_output_directory(self) # Call the function from ui_utils
        if self.output_dir:
            self.output_label.setText(f'Output: {self.output_dir}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs' # Use pathlib for cleaner path handling
        configs = load_config_options(config_dir)  # Call from ui_utils
        self.config_combo.addItems(configs)
        self.config_combo.currentIndexChanged.connect(self.update_config_file) # Get the config
def update_config_file(self, index):
        self.config_file = self.config_combo.itemText(index)
def process_pdfs(self):
        process_pdfs(self.input_dir, self.output_dir, self.config_file, self.progress_bar) # Call from ui_utils



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())

def __init__(self):
        super().__init__()
        self.config_file = ""  # Initialize config_file
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select')
        self.input_btn.clicked.connect(self.select_input_directory)  # Connect to ui_utils function
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_btn)

        # Output directory
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select')
        self.output_btn.clicked.connect(self.select_output_directory) # Connect to ui_utils function
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_btn)

        # Config selection
        self.config_combo = QComboBox()
        self.load_configs()
        layout.addWidget(QLabel('Config File:'))
        layout.addWidget(self.config_combo)

        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)  # Connect to ui_utils function
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
def select_input_directory(self):
        self.input_dir = select_input_directory(self) # Call the function from ui_utils
        if self.input_dir:
            self.input_label.setText(f'Input: {self.input_dir}')
def select_output_directory(self):
        self.output_dir = select_output_directory(self) # Call the function from ui_utils
        if self.output_dir:
            self.output_label.setText(f'Output: {self.output_dir}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs' # Use pathlib for cleaner path handling
        configs = load_config_options(config_dir)  # Call from ui_utils
        self.config_combo.addItems(configs)
        self.config_combo.currentIndexChanged.connect(self.update_config_file) # Get the config
def update_config_file(self, index):
        self.config_file = self.config_combo.itemText(index)
def process_pdfs(self):
        process_pdfs(self.input_dir, self.output_dir, self.config_file, self.progress_bar) # Call from ui_utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())

def __init__(self):
        super().__init__()
        self.config_file = ""  # Initialize config_file
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select')
        self.input_btn.clicked.connect(self.select_input_directory)  # Connect to ui_utils function
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_btn)

        # Output directory
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select')
        self.output_btn.clicked.connect(self.select_output_directory) # Connect to ui_utils function
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_btn)

        # Config selection
        self.config_combo = QComboBox()
        self.load_configs()
        layout.addWidget(QLabel('Config File:'))
        layout.addWidget(self.config_combo)

        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)  # Connect to ui_utils function
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
def select_input_directory(self):
        self.input_dir = select_input_directory(self) # Call the function from ui_utils
        if self.input_dir:
            self.input_label.setText(f'Input: {self.input_dir}')
def select_output_directory(self):
        self.output_dir = select_output_directory(self) # Call the function from ui_utils
        if self.output_dir:
            self.output_label.setText(f'Output: {self.output_dir}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs' # Use pathlib for cleaner path handling
        configs = load_config_options(config_dir)  # Call from ui_utils
        self.config_combo.addItems(configs)
        self.config_combo.currentIndexChanged.connect(self.update_config_file) # Get the config
def update_config_file(self, index):
        self.config_file = self.config_combo.itemText(index)
def process_pdfs(self):
        process_pdfs(self.input_dir, self.output_dir, self.config_file, self.progress_bar) # Call from ui_utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""  # Initialize config_file
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select')
        self.input_btn.clicked.connect(self.select_input_directory)  # Connect to ui_utils function
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_btn)

        # Output directory
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select')
        self.output_btn.clicked.connect(self.select_output_directory) # Connect to ui_utils function
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_btn)

        # Config selection
        self.config_combo = QComboBox()
        self.load_configs()
        layout.addWidget(QLabel('Config File:'))
        layout.addWidget(self.config_combo)

        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)  # Connect to ui_utils function
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
def select_input_directory(self):
            self.input_dir = select_input_directory(self) # Call the function from ui_utils
            if self.input_dir:
                self.input_label.setText(f'Input: {self.input_dir}')
def select_output_directory(self):
            self.output_dir = select_output_directory(self) # Call the function from ui_utils
            if self.output_dir:
                self.output_label.setText(f'Output: {self.output_dir}')
def load_configs(self):
            config_dir = Path(__file__).parent / 'scripts' / 'configs' # Use pathlib for cleaner path handling
            configs = load_config_options(config_dir)  # Call from ui_utils
            self.config_combo.addItems(configs)
            self.config_combo.currentIndexChanged.connect(self.update_config_file) # Get the config
def update_config_file(self, index):
            self.config_file = self.config_combo.itemText(index)
def process_pdfs(self):
            process_pdfs(self.input_dir, self.output_dir, self.config_file, self.progress_bar) # Call from ui_utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
def __init__(self):
        super().__init__()
        self.config_file = ""  # Initialize config_file
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()
def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        self.input_label = QLabel('Input Directory:')
        self.input_btn = QPushButton('Select')
        self.input_btn.clicked.connect(self.select_input_directory)  # Connect to ui_utils function
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_btn)

        # Output directory
        self.output_label = QLabel('Output Directory:')
        self.output_btn = QPushButton('Select')
        self.output_btn.clicked.connect(self.select_output_directory) # Connect to ui_utils function
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_btn)

        # Config selection
        self.config_combo = QComboBox()
        self.load_configs() 
        layout.addWidget(QLabel('Config File:'))
        layout.addWidget(self.config_combo)

        # Process button
        self.process_btn = QPushButton('Process PDFs')
        self.process_btn.clicked.connect(self.process_pdfs)  # Connect to ui_utils function
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('PDF Processor')
def select_input_directory(self):
        self.input_dir = select_input_directory(self) # Call the function from ui_utils
        if self.input_dir:
            self.input_label.setText(f'Input: {self.input_dir}')
def select_output_directory(self):
        self.output_dir = select_output_directory(self) # Call the function from ui_utils
        if self.output_dir:
            self.output_label.setText(f'Output: {self.output_dir}')
def load_configs(self):
        config_dir = Path(__file__).parent / 'scripts' / 'configs' # Use pathlib for cleaner path handling
        configs = load_config_options(config_dir)  # Call from ui_utils
        self.config_combo.addItems(configs)
        self.config_combo.currentIndexChanged.connect(self.update_config_file) # Get the config
def update_config_file(self, index):
        self.config_file = self.config_combo.itemText(index)
def process_pdfs(self):
        process_pdfs(self.input_dir, self.output_dir, self.config_file, self.progress_bar) # Call from ui_utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SimpleUI()
    ui.show()
    sys.exit(app.exec())
