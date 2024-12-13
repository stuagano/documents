import os
import re
import sys
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from utils.extract_utils import extract_text_from_bbox
from utils.precondition_checker import check_for_signature

def extract_financial_info(img, client_profile_box, tax_bracket_checkbox_coords, account_number = None, account_name = None):
    """Extracts financial info, Tax Bracket determined by checkbox."""
    x, y, width, height = client_profile_box  
    cropped_img = img.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip()
    info = {}
    if account_number:
        info["Account Number"] = account_number
    if account_name:
        info["Account Name"] = account_name

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

def is_checkbox_checked(img, x, y, width, height):
    """Determine if a checkbox is checked based on the image region."""
    cropped_img = img.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip()
    return bool(text)  # Adjust based on how the checkbox state is represented
    """Extracts financial info, Tax Bracket determined by checkbox."""
    x, y, width, height = client_profile_box  
    cropped_img = img.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip()
    info = {}

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

def process_pdf(pdf_path, output_directory, client_profile_box, tax_bracket_checkbox_coords):
    """Processes a single PDF to extract financial information."""
    images = convert_from_path(pdf_path)
    for img in images:
        info = extract_financial_info(img, client_profile_box, tax_bracket_checkbox_coords)
        if info:
            with open(os.path.join(output_directory, 'financial_info.txt'), 'a') as f:
                f.write(f"PDF: {os.path.basename(pdf_path)}\n")
                for key, value in info.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

def main(input_directory, output_directory):
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)

    client_profile_box = (200, 600, 900, 500)  # Adjust as needed
    tax_bracket_checkbox_coords = (100, 150, 20, 20)  # Example coordinates

    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing: {pdf_path}")
            try:
                process_pdf(pdf_path, output_directory, client_profile_box, tax_bracket_checkbox_coords)
                print(f"Successfully processed: {filename}\n")
            except Exception as e:
                print(f"Error processing {filename}: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Client_Profile.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)




