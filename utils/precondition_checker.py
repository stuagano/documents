import pytesseract
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QMessageBox

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

def precondition_check(images, parent=None):
    """
    Check preconditions on the PDF document.
    """
    try:
        if not images or len(images) == 0:
            raise ValueError("No images provided for precondition check")

        results = {}
        precondition_status = {}
        
        # Extract account info from first page
        first_page = images[0]
        
        # Define regions for account info (adjust as needed)
        account_number_bbox = (450, 50, 150, 30)
        account_name_bbox = (50, 50, 300, 30)
        
        # Extract text from regions
        account_number = extract_text_from_bbox(first_page, account_number_bbox)
        account_name = extract_text_from_bbox(first_page, account_name_bbox)
        
        # Store results
        results["Account Number"] = account_number
        results["Account Name"] = account_name
        
        # Check presence
        precondition_status["Account Number Present"] = bool(account_number)
        precondition_status["Account Name Present"] = bool(account_name)
        
        # Store status
        results["Precondition Status"] = precondition_status
        
        # Show results in GUI if parent provided
        if parent and (not account_number or not account_name):
            QMessageBox.warning(
                parent,
                "Precondition Check Failed",
                f"Missing required information:\nAccount Number: {'Found' if account_number else 'Missing'}\nAccount Name: {'Found' if account_name else 'Missing'}"
            )
        
        return results

    except Exception as e:
        print(f"Precondition check failed: {e}")
        if parent:
            QMessageBox.critical(parent, "Error", f"Precondition check failed: {e}")
        return {
            "Account Number": "",
            "Account Name": "",
            "Precondition Status": {
                "Account Number Present": False,
                "Account Name Present": False
            }
        }