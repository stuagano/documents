# FILE:SIMPLE_UI.PY

import sys
import os
import json
import re
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout, QDialog, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import importlib.util
from scripts.display_utils import display_image_with_boxes  # Ensure this utility is available

def load_script_module(script_path):
    spec = importlib.util.spec_from_file_location("script_module", script_path)
    script_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script_module)
    return script_module

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
        self.setLayout(layout)

class SimpleUI(QWidget):
    def __init__(self):
        super().__init__()
        # Get the directory containing simple_ui.py
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        
        print(f"Base directory: {self.base_dir}")
        print(f"Scripts directory: {self.scripts_dir}")
        
        # Verify scripts directory exists
        if not os.path.exists(self.scripts_dir):
            QMessageBox.warning(self, 'Warning', f'Scripts directory not found at: {self.scripts_dir}')
            return
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simple Script Runner')
        self.setGeometry(100, 100, 1000, 700)  # Increased size for better image viewing

        layout = QVBoxLayout()

        # Script selection
        self.script_label = QLabel('Available Scripts:', self)
        layout.addWidget(self.script_label)
        
        self.script_list = QListWidget(self)
        self.populate_script_list()
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

        # Image display area (Removed from main window)

        # Process PDF button
        self.btn_process = QPushButton('Process PDF', self)
        self.btn_process.clicked.connect(self.process_pdf)
        layout.addWidget(self.btn_process)

        self.setLayout(layout)

        # Initialize directories and PDF path
        self.input_directory = ''
        self.output_directory = ''
        self.pdf_file = ''

    def populate_script_list(self):
        try:
            scripts = [f for f in os.listdir(self.scripts_dir) if f.endswith('.py')]
            if scripts:
                self.script_list.addItems(scripts)
            else:
                QMessageBox.information(self, 'Info', 'No scripts found in the scripts directory.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading scripts: {e}')

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

    def select_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF File', '', 'PDF Files (*.pdf)')
        if file_path:
            self.pdf_file = file_path
            self.pdf_path.setText(file_path)

    def process_pdf(self):
        if not self.input_directory or not self.output_directory or not self.pdf_file:
            QMessageBox.warning(self, 'Warning', 'Please select input directory, output directory, and PDF file.')
            return
        selected_script_item = self.script_list.currentItem()
        if not selected_script_item:
            QMessageBox.warning(self, 'Warning', 'Please select a script to run.')
            return
        selected_script = selected_script_item.text()
        script_path = os.path.join(self.scripts_dir, selected_script)
        try:
            script_module = load_script_module(script_path)
            print(f"Loaded script: {selected_script}")
            bounding_boxes = script_module.bounding_boxes  # Ensure each script defines `bounding_boxes`
            page_number = bounding_boxes["page_number"]
            boxes = bounding_boxes["boxes"]
            print(f"Bounding boxes: {bounding_boxes}")
            
            images = convert_from_path(self.pdf_file, dpi=300)
            if page_number > len(images):
                QMessageBox.warning(self, 'Warning', f'Page {page_number} does not exist in the PDF.')
                return
            
            page_image = images[page_number - 1].convert('RGB')
            
            # Display image with bounding boxes
            display_image_with_boxes(page_image.copy(), boxes)
            
            # Ask for user confirmation
            reply = QMessageBox.question(
                self, 
                'Confirm Bounding Boxes',
                'Are the bounding boxes correct?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Proceed with extraction
                extracted_data = script_module.extract_data(page_image, boxes)
                print(f"Extracted data: {extracted_data}")
                
                # Save extracted data
                output_file = os.path.join(self.output_directory, f'{os.path.splitext(os.path.basename(self.pdf_file))[0]}_FeeToBeCharged.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(extracted_data, f, indent=4)
                
                QMessageBox.information(self, 'Success', f'Extracted data saved to {output_file}')
            else:
                QMessageBox.warning(self, 'Cancelled', 'Extraction cancelled by user.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to process PDF: {e}')
            print(f"Error: {e}")
            
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