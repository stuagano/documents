import pytesseract
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QMessageBox
import json
import os

def extract_text_from_bbox(image, bbox):
    """Extract text from a specific region of the image."""
    try:
        x, y, width, height = bbox
        cropped = image.crop((x, y, x + width, y + height))
        return pytesseract.image_to_string(cropped).strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def check_for_signature(image, bbox):
    """Check for presence of signature in image region."""
    try:
        x, y, width, height = bbox
        cropped = image.crop((x, y, x + width, y + height))
        grayscale = cropped.convert('L')
        text = pytesseract.image_to_string(grayscale).strip()
        return bool(text)
    except Exception as e:
        print(f"Error checking signature: {e}")
        return False

def has_docusign_signature(image):
    """
    Checks if an image contains a DocuSign signature.

    Args:
        image (PIL.Image.Image): The image to check.

    Returns:
        bool: True if a DocuSign signature is found, False otherwise.
    """
    text = pytesseract.image_to_string(image).strip()
    return "DocuSign" in text

def run_precondition_checks(config_path, images):
    """
    Runs precondition checks based on the config file and images.

    Args:
        config_path (str): Path to the config.json file.
        images (list): List of PIL Image objects representing the PDF pages.

    Returns:
        list: A list of dictionaries containing the results of the checks for each PDF.
    """

    results = []

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        for image in images:
            document_results = {}
            for field, data in config.items():
                page_number = data.get('page', 1) - 1  # Adjust to 0-based indexing
                bbox = data.get('bbox')

                if page_number < len(images) and bbox:
                    extracted_text = extract_text_from_bbox(images[page_number], bbox)
                    document_results[field] = extracted_text

                    # Apply preconditions based on field name (example)
                    if field == 'owner_initials_page_1_2':
                        # Check if one or two sets of initials are present
                        document_results[field + '_check'] = bool(extracted_text) 
                    # Add more precondition checks as needed

                # Check for DocuSign signature on specified pages
                if 'docusign_pages' in data and page_number in data['docusign_pages']:
                    has_signature = has_docusign_signature(images[page_number])
                    document_results['docusign_signature_check'] = has_signature

            results.append(document_results)

    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        # Handle file not found error, e.g., show a message box
        # QMessageBox.critical(None, "Error", f"Config file not found: {config_path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        # Handle invalid JSON error
        # QMessageBox.critical(None, "Error", f"Invalid JSON in config file: {config_path}")
    except Exception as e:
        print(f"Error during precondition checks: {e}")
        # Handle other exceptions
        # QMessageBox.critical(None, "Error", f"Error during precondition checks: {e}")

    # Count failed documents
    failed_documents = 0
    for document_result in results:
        if not all(document_result.get(field + '_check', True) for field in config):  
            failed_documents += 1

    # Report failed documents to the user
    if failed_documents > 0:
        print(f"Precondition checks failed for {failed_documents} documents.")
        # Show message box to user
        # QMessageBox.warning(None, "Precondition Check Warning",
        #                     f"Precondition checks failed for {failed_documents} documents. Do you want to continue?")

    return results