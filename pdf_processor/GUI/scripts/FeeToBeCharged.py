# FeeToBeCharged.py

import pytesseract
from PIL import Image
import re

# Define bounding boxes and the page number
bounding_boxes = {
    "page_number": 10,  # Page 10
    "boxes": [
        (450, 750, 400, 200),  # Fee to be Charged
        # Add other boxes here if needed
    ]
}

def extract_fee(text):
    """Extracts the fee percentage."""
    # Enhanced regex pattern to capture various formats of the fee
    pattern = r"Fee\s*to\s*be\s*[\(\)\|,]*\s*([\d\.]+%)|([\d\.]+)\s*%|([\d\.]+)\s*percent|([\d\.]+)\s*management\s*fee"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        fee = match.group(1) or match.group(2) or match.group(3) or match.group(4)
        fee = fee.replace(",", ".").replace("J", "0")
        
        # Normalize the fee to a small management fee percentage if necessary
        try:
            fee_value = float(fee.strip('%'))
            if fee_value > 2.25:  # Assuming management fees are typically less than 2.25%
                fee_value = fee_value / 100
            fee = f"{fee_value:.2f}%"
        except ValueError:
            print(f"DEBUG: Invalid fee value extracted: {fee}")
            return None
        
        print(f"DEBUG: Fee found: {fee}")
        return fee
    else:
        print(f"DEBUG: Fee pattern not found in text:\n---\n{text}\n---")
        return None

def extract_data(page_image, boxes):
    """
    Extracts fee data from the specified bounding boxes on the given page image.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).

    Returns:
        dict: Extracted fee data.
    """
    extracted_data = {}
    raw_texts = {}
    for box in boxes:
        x, y, width, height = box
        cropped_img = page_image.crop((x, y, x + width, y + height))
        text = pytesseract.image_to_string(cropped_img).strip()
        raw_texts[f"Box {box}"] = text  # Store raw text for debugging
        fee = extract_fee(text)
        if fee:
            extracted_data["Fee to Be Charged"] = fee
        else:
            extracted_data["Fee to Be Charged"] = "Not found"
    
    extracted_data["Raw Texts"] = raw_texts  # Include raw texts in the output
    return extracted_data