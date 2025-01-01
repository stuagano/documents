import sys
from pathlib import Path  # For config path handling
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QProgressBar, QComboBox
)
from ui_utils import ( # Import *only* what you need
    load_config_options, select_input_directory, select_output_directory, process_pdfs
)

class SimpleUI(QWidget):
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