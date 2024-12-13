# page12.py

import pytesseract
from PIL import Image
import json
from pdf_processor.utils.precondition_checker import extract_text_from_bbox
from pdf_processor.utils.precondition_checker import check_for_signature

# Define bounding boxes and the page number
bounding_boxes = {
    "page_number": 12,
    "boxes": [
        (300, 100, 200, 100),   # Advisor Signature (centered towards the top)
        (100, 300, 800, 100),   # Client Name (left aligned, full page width)
        (100, 450, 800, 100),   # Client Signature (left aligned, full page width)
        # Add other boxes if needed
    ]
}

def extract_data(page_image, boxes, account_number, account_name):
    """
    Extracts data from the specified bounding boxes on the given page image,
    including Account Number and Account Name with signature verification status.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        account_number (str): Extracted account number from Page 1.
        account_name (str): Extracted account name from Page 1.

    Returns:
        dict: Extracted data including Account Number and Account Name.
    """
    extracted_data = {
        "Account Number": account_number,
        "Account Name": account_name
    }
    for box in boxes:
        x, y, width, height = box
        text = extract_text_from_bbox(page_image, box)
        
        if box == (300, 100, 200, 100):
            # Advisor Signature
            extracted_data["Advisor Signature Text"] = text
            signature_present = check_for_signature(page_image, box)
            extracted_data["Advisor Signature Present"] = "Yes" if signature_present else "No"
        
        elif box == (100, 300, 800, 100):
            # Client Name
            extracted_data["Client Name"] = text
        
        elif box == (100, 450, 800, 100):
            # Client Signature
            extracted_data["Client Signature Text"] = text
            signature_present = check_for_signature(page_image, box)
            extracted_data["Client Signature Present"] = "Yes" if signature_present else "No"
        
        # Add other conditional extractions as needed

    return extracted_data