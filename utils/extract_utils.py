import pytesseract
from PIL import Image
import re
from pdf_processor.pdf_processor.GUI.scripts.utils.extract_utils import extract_text_from_bbox
from pdf_processor.pdf_processor.GUI.scripts.utils.precondition_checker import check_for_signature

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

def display_image_with_boxes(image, boxes, labels=None):
    """
    Draws bounding boxes on the image for visualization.

    Args:
        image (PIL.Image.Image): The image to draw boxes on.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        labels (list of str, optional): Labels for each bounding box.
    """
    draw = ImageDraw.Draw(image)
    for i, box in enumerate(boxes):
        x, y, width, height = box
        draw.rectangle([x, y, x + width, y + height], outline="red", width=2)
        if labels and i < len(labels):
            draw.text((x, y - 10), labels[i], fill="red")
    return image    

def pil_to_pixmap(pil_image):
    """Convert PIL Image to QPixmap."""
    if pil_image.mode == "RGBA":
        qim = QImage(pil_image.tobytes("raw", "RGBA"), pil_image.size[0],
                    pil_image.size[1], QImage.Format_RGBA8888)
    else:
        qim = QImage(pil_image.tobytes("raw", "RGB"), pil_image.size[0],
                    pil_image.size[1], QImage.Format_RGB888)
    return QPixmap.fromImage(qim)