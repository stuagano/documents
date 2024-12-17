# FILE:SIMPLE_UI.PY

import sys
import os

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
from PyQt5.QtGui import QPixmap, QImage, QPen, QColor
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, UnidentifiedImageError
import pytesseract
import importlib.util
import logging
import tempfile
import csv
import pandas as pd
from skimage.metrics import structural_similarity as ssim

from pdf_processor.logic.pdf_processor import (  # Importing from pdf_processor.py
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

    def __init__(self):
        super().__init__()
        # Get the directory containing simple_ui.py
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Add current_image attribute to store the loaded image
        self.current_image = None

        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        
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
                QMessageBox.warning(self, 'Warning', 'No config files found in the configs directory.')
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
                    QMessageBox.warning(self, 'Warning', 'No config files found to select.')
                    logging.warning("No config files found to select.")
        except Exception as e:  # Handle potential exceptions during file listing
            QMessageBox.critical(self, "Error", f"An error occurred during config file loading: {e}")
            logging.exception("An error occurred during config file loading: %s", e)       

            # Image display area (Removed from main window)

        # Process PDF button
        self.btn_process = QPushButton('Process PDF', self)
        self.btn_process.clicked.connect(self.process_pdf)
        layout.addWidget(self.btn_process)

        self.setLayout(layout)

        # Initialize directories and PDF path
        self.input_directory = ''
        self.output_directory = ''
        self.previous_image_path = None  # Store path to previous image
        
        self.pdf_file = ''
        # Add config_file attribute
        self.config_file = '' 

    def display_dataframe_head(self, df):

        """Prints the first 5 rows of the DataFrame to the console."""
        print("DataFrame Head:")
        print(df.head())

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
            self.current_image = images[0]  # Store the first image for later use

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
                self.current_image.save(temp_file.name)
                self.previous_image_path = temp_file.name

            # Run the precondition checker before processing
            precondition_results = precondition_check(images)
            self.display_dataframe_head(pd.DataFrame(precondition_results))            
            extracted_data = extract_data_from_pdf(self.pdf_file, self.config_file)
            print(extracted_data)
            
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleUI()
    ex.show()
    sys.exit(app.exec_())