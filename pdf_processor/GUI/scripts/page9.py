import pytesseract
from PIL import Image
import json
import re

# Define bounding boxes and the page number
bounding_boxes = {
    "page_number": 9,
    "boxes": [
        (200, 300, 400, 50),  # Box for "Name(s):"
        # Add other boxes if needed
    ]
}

def extract_text_right_of_names(text):
    """Extracts the text to the right of 'Name(s):'."""
    match = re.search(r"Name\(s\):\s*(.+)", text)
    if match:
        return match.group(1).strip()
    return "Not found"

def extract_data(page_image, boxes):
    """
    Extracts data from the specified bounding boxes on the given page image.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).

    Returns:
        dict: Extracted data.
    """
    extracted_data = {}
    for box in boxes:
        x, y, width, height = box
        cropped_img = page_image.crop((x, y, x + width, y + height))
        text = pytesseract.image_to_string(cropped_img).strip()
        if box == (200, 300, 400, 50):
            extracted_data["Name(s)"] = extract_text_right_of_names(text)
        # Add other conditional extractions as needed
    return extracted_data