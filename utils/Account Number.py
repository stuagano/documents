# Account_Number.py

import pytesseract
from PIL import Image
import re

bounding_boxes = {
    "page_number": 10,  # Page number where account info is located
    "boxes": [
        (450, 750, 400, 200),  # Account Number Box
    ]
}

def extract_account_number(text):
    """Extracts account number in the format GCWXXXXXX from text."""
    pattern = r"GCW\d{6}"
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_data(page_image, boxes):
    """
    Extracts account number from the specified bounding boxes on the given page image.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).

    Returns:
        dict: Extracted account number.
    """
    extracted_data = {}
    for box in boxes:
        x, y, width, height = box
        cropped_img = page_image.crop((x, y, x + width, y + height))
        text = pytesseract.image_to_string(cropped_img).strip()
        account_number = extract_account_number(text)
        extracted_data["Account Number"] = account_number
    return extracted_data