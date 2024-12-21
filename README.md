# PDF Processor with GUI

This project provides a graphical user interface (GUI) for processing PDF documents.  It allows users to extract specific information, perform validation checks, and manipulate PDF content.

## Project Setup

1. **Clone the Repository:**
```
bash
   git clone <repository_url>
   cd <project_directory>
   
```
2. **Install Dependencies:**
```
bash
   pip install -r requirements.txt
   
```
## Usage Instructions

1. **Run the GUI:**
```
bash
   python pdf_processor/GUI/simple_ui.py
   
```
This will launch the graphical interface.

2. **Load a PDF:** Use the file selection dialog within the GUI to choose the PDF you want to process.


3. **Process the PDF:** The GUI will offer various processing options. Select the desired operation and click "Process." The program will then output the result in the designated area.


## Configuration Files

The project uses several configuration files located in `pdf_processor/GUI/scripts/configs/`:

* `account_profile_config.json`: Configuration for account profile processing.
* `clientprofile.json`:  Configuration for client profile extraction.
* `complianceDisclosureDelivery_config.json`: Configuration for compliance disclosure processing.
* ... (other configuration files)

Each configuration file specifies details about the data to extract from specific pages or sections of the PDF.  Modify these files to adjust the extraction logic according to the format of your input PDFs.  Refer to the individual configuration file comments for specific options and examples.

## Module Structure

The project's core PDF processing logic has been moved to a separate module for better organization and reusability.  The `pdf_processor/pdf_processing.py` module contains the following key functions:

* `validate_config(config_path)`: Validates the configuration file.
* `read_config(config_path)`: Reads and parses the configuration file.
* `extract_text_from_bbox(image, bbox)`: Extracts text from a specified bounding box within an image.
* `process_pdf(pdf_path, config, investment_experience_type)`: Processes a single PDF file based on the provided configuration.

This modular structure allows for easier maintenance, testing, and potential reuse of these functions in other projects.

## Running Tests

To run the test suite:
```
bash
python -m unittest discover tests
```
## Special Considerations

* **Dependencies:** Ensure that all dependencies listed in `requirements.txt` are installed.  Some PDF processing libraries may require additional system libraries.
* **PDF Structure:** The extraction logic depends heavily on the structure of the input PDFs.  If the format changes, you may need to adjust the configuration files accordingly.  
* **Error Handling:** The application includes error handling, but unexpected PDF formats may still cause issues.  Check the logs and output for errors.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.  Follow the established contribution guidelines if provided.


## Additional Notes

* For detailed information on the processing logic, refer to the individual Python scripts in the `pdf_processor/GUI/scripts` directory.
* The project is designed for... (mention target use cases/users).
* ... (Add more notes about potential issues, future developments, etc.)