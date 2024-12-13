import pytesseract
from PIL import Image
import re
from pdf_processor.pdf_processor.GUI.scripts.utils.extract_utils import extract_text_from_bbox, extract_emails
from pdf_processor.pdf_processor.GUI.scripts.utils.precondition_checker import check_for_signature

# Define bounding boxes and the page number
bounding_boxes = {
    "page_number": 5,
    "boxes": [
        (100, 150, 200, 50),   # Annual Delivery of Privacy Policy
        (100, 220, 200, 50),   # Annual Delivery of Form ADV
        (100, 290, 200, 50),   # Other
        (350, 150, 500, 50),   # Email Addresses
        (350, 220, 500, 100),  # Additional Signature
        # Add other boxes if needed
    ]
}

def is_checkbox_checked(text):
    """
    Determines if a checkbox is checked based on the recognized text.

    Args:
        text (str): The OCR-extracted text from the checkbox area.

    Returns:
        bool: True if the checkbox is checked, False otherwise.
    """
    # Common indicators of a checked box
    checked_indicators = ['x', '✓', '✔', 'yes', 'checked']
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in checked_indicators)

def extract_data(page_image, boxes, account_number, account_name):
    """
    Extracts compliance disclosure data from the specified bounding boxes on the given page image,
    including account details, checkbox statuses, email addresses, and an additional signature check.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        account_number (str): Extracted account number from Page 1.
        account_name (str): Extracted account name from Page 1.

    Returns:
        dict: Extracted compliance disclosure data.
    """
    extracted_data = {
        "Account Number": account_number,
        "Account Name": account_name
    }
    raw_texts = {}
    
    # Initialize fields
    extracted_data["Annual Delivery of Privacy Policy"] = False
    extracted_data["Annual Delivery of Form ADV"] = False
    extracted_data["Other"] = False
    extracted_data["Email Addresses"] = []
    extracted_data["Additional Signature Present"] = False

    for box in boxes:
        x, y, width, height = box
        cropped_img = page_image.crop((x, y, x + width, y + height))
        text = pytesseract.image_to_string(cropped_img).strip()
        raw_texts[f"Box {box}"] = text  # Store raw text for debugging

        # Determine which box this is based on coordinates
        if box == (100, 150, 200, 50):
            # Annual Delivery of Privacy Policy
            extracted_data["Annual Delivery of Privacy Policy"] = is_checkbox_checked(text)
        
        elif box == (100, 220, 200, 50):
            # Annual Delivery of Form ADV
            extracted_data["Annual Delivery of Form ADV"] = is_checkbox_checked(text)
        
        elif box == (100, 290, 200, 50):
            # Other
            extracted_data["Other"] = is_checkbox_checked(text)
        
        elif box == (350, 150, 500, 50):
            # Email Addresses
            emails = extract_emails(text)
            extracted_data["Email Addresses"].extend(emails)
        
        elif box == (350, 220, 500, 100):
            # Additional Signature
            # Perform signature check using precondition_checker utility
            # Since signatures are images, we might need to pass the bounding box to the checker
            # However, in this context, we assume text-based signature presence
            # For image-based signature checks, additional implementation is needed
            # Here, we'll check if there's any text indicating a signature
            signature_present = is_checkbox_checked(text) or bool(text)
            extracted_data["Additional Signature Present"] = signature_present
        
        # Add other conditional extractions as needed

    extracted_data["Raw Texts"] = raw_texts  # Include raw texts in the output
    return extracted_data
