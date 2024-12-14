import re
import pytesseract
from PIL import Image
import numpy as np

"""Utility functions for PDF processing, OCR, and text extraction."""


from PIL import Image, ImageDraw

def is_checkbox_checked(img, x, y, width, height):
    """
    Determines if a checkbox is checked based on the recognized text.

    Args:
        img (PIL.Image): The image containing the checkbox.
        x (int): The x-coordinate of the top-left corner of the checkbox.
        y (int): The y-coordinate of the top-left corner of the checkbox.
        width (int): The width of the checkbox.
        height (int): The height of the checkbox.

    Returns:
        bool: True if the checkbox is checked, False otherwise.
    """
    cropped_img = img.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip().lower()
    checked_indicators = ['x', '✓', '✔', 'yes', 'checked']
    return any(indicator in text for indicator in checked_indicators)

def extract_emails(text):
    """
    Extracts email addresses from the given text.

    Args:
        text (str): The OCR-extracted text containing email addresses.

    Returns:
        list: A list of extracted email addresses.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return re.findall(email_pattern, text)

def extract_financial_info(img, client_profile_box, tax_bracket_checkbox_coords, account_number, account_name):
    """Extracts financial info, Tax Bracket determined by checkbox."""
    x, y, width, height = client_profile_box  
    cropped_img = img.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip()
    info = {
        "Account Number": account_number,
        "Account Name": account_name
    }

    patterns = { 
        "Annual Income": r"Annual Income:\s*([$0-9,]+(?:\s*-\s*[$0-9,]+)?)",
        "Net Worth": r"Net Worth:\s*([$0-9,]+(?:\s*-\s*[$0-9,]+)?)",
        "Liquid Net Worth": r"Liquid Net Worth:\s*([$0-9,]+(?:\s*-\s*[$0-9,]+)?)",
    }

    for keyword, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info[keyword] = match.group(1)
        else:
            info[keyword] = None       

    checkbox_x, checkbox_y, checkbox_width, checkbox_height = tax_bracket_checkbox_coords
    if is_checkbox_checked(img, checkbox_x, checkbox_y, checkbox_width, checkbox_height):
        info["Tax Bracket"] = "0-24%" 
    else:
        info["Tax Bracket"] = "25%+"

    return info

def display_image_with_boxes(image, boxes, title="Image with Bounding Boxes"):
    """
    Displays the image with bounding boxes.

    Args:
        image (PIL.Image.Image): The image to display.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        title (str): Title of the image window.
    """
    draw = ImageDraw.Draw(image)
    for box in boxes:
        x, y, width, height = box
        draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=2)
    image.show(title=title)

    
def extract_text_from_bbox(image, bbox):
    """Extract text from a bounding box region."""
    x, y, width, height = bbox
    cropped = image.crop((x, y, x + width, y + height))
    return pytesseract.image_to_string(cropped).strip()

def is_checkbox_checked(text):
    """Check if checkbox contains a mark."""
    checked_indicators = ['x', '✓', '✔', 'yes', 'checked']
    return any(indicator in text.lower() for indicator in checked_indicators)

def extract_emails(text):
    """Extract email addresses from text."""
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return re.findall(email_pattern, text)

def check_for_signature(image, bbox):
    """Check for presence of signature."""
    x, y, width, height = bbox
    cropped = image.crop((x, y, x + width, y + height))
    grayscale = cropped.convert('L')
    text = pytesseract.image_to_string(grayscale).strip()
    return bool(text)

def extract_account_info(text):
    """
    Extract account number and name from text.
    
    Args:
        text (str): Text containing account information
        
    Returns:
        dict: Dictionary containing account number and name
    """
    account_number_pattern = r"GCW\d{6}"
    account_name_pattern = r"Name\(s\):\s*(.+)"
    
    account_number = None
    account_name = None
    
    number_match = re.search(account_number_pattern, text)
    if number_match:
        account_number = number_match.group(0)
        
    name_match = re.search(account_name_pattern, text)
    if name_match:
        account_name = name_match.group(1).strip()
        
    return {
        "Account Number": account_number,
        "Account Name": account_name
    }

def extract_investment_data(text):
    """Extract investment related data from text."""
    patterns = {
        "Investment Experience": r"Investment\s*Experience[:.]?\s*([^\n]+)",
        "Risk Tolerance": r"Risk\s*Tolerance[:.]?\s*([^\n]+)",
        "Time Horizon": r"Time\s*Horizon[:.]?\s*([^\n]+)"
    }
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        results[key] = match.group(1).strip() if match else None
    return results

def validate_extracted_data(data, required_fields):
    """Validate that required fields are present in extracted data."""
    missing = []
    for field in required_fields:
        if not data.get(field):
            missing.append(field)
    return {"valid": len(missing) == 0, "missing_fields": missing}

__all__ = [
    'extract_text_from_bbox',
    'is_checkbox_checked',
    'extract_emails',
    'check_for_signature',
    'extract_account_info',
    'extract_investment_data',
    'validate_extracted_data'
]