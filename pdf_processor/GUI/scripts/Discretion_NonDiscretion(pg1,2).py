#!/usr/bin/env python
# coding: utf-8
import fitz
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from utils.base_utils import extract_text_from_bbox
from utils.display_utils import display_image_with_boxes


def has_docusign_signature(pdf_path):
    """
    Checks if a PDF page has a DocuSign signature.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        bool: True if a DocuSign signature is likely present, False otherwise.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            if "DocuSign" in text:
                return True
        return False
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def process_pdf(pdf_path, output_directory):
    """
    Processes a PDF to extract account info and check for initials.

    Args:
        pdf_path (str): The path to the PDF file.
        output_directory (str): The directory to save the results.
    """
    # Open the PDF document
    pdf_document = fitz.open(pdf_path)

    # Define bounding boxes in the format (x, y, width, height)
    # Adjust the coordinates as needed based on your PDF
    account_number_bbox = (450, 50, 150, 30)  # Top-right of page 1
    account_name_bbox = (50, 50, 300, 30)     # Adjust coordinates as needed

    # Convert page 1 to image
    page_number = 1
    page = pdf_document.load_page(page_number - 1)
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Display image with bounding boxes and ask for confirmation
    boxes = [account_number_bbox, account_name_bbox]
    labels = ["Account Number", "Account Name"]
    display_image_with_boxes(img.copy(), boxes, labels)

    # Ask for user confirmation
    user_input = input("Are the bounding boxes correctly placed? (y/n): ")
    if user_input.lower() != 'y':
        print("Please adjust the bounding boxes in the script and try again.")
        return

    # Extract account number and account name
    account_number = extract_text_from_bbox(img, account_number_bbox)
    account_name = extract_text_from_bbox(img, account_name_bbox)

    # Check for initials on pages 1 and 2
    initials_info = check_for_initials(pdf_document, page_numbers=[1, 2])

    # Compile results
    result = {
        "PDF": os.path.basename(pdf_path),
        "Account Number": account_number,
        "Account Name": account_name,
        "Initials Found": initials_info["total_initials"],
        "Pages with Initials": initials_info["pages_with_initials"]
    }

    # Save results to CSV
    result_file = os.path.join(output_directory, 'discretion_nondiscretion_results.csv')
    write_results_to_csv(result_file, result)

def write_results_to_csv(file_path, result):
    import csv
    header = ["PDF", "Account Number", "Account Name", "Initials Found", "Pages with Initials"]
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

def display_image_with_boxes(image, boxes, labels):
    """
    Displays the image with bounding boxes for user confirmation.

    Args:
        image (PIL.Image.Image): The image to display.
        boxes (list): List of bounding boxes (x, y, width, height).
        labels (list): List of labels corresponding to the boxes.
    """
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    for bbox, label in zip(boxes, labels):
        x, y, width, height = bbox
        rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        ax.text(x, y - 10, label, color='red', fontsize=12)
    plt.axis('off')
    plt.show()

def extract_text_from_bbox(image, bbox):
    """
    Extracts text from a given bounding box in the image.

    Args:
        image (PIL.Image.Image): The image to extract text from.
        bbox (tuple): The bounding box (x, y, width, height).

    Returns:
        str: The extracted text.
    """
    x, y, width, height = bbox
    cropped_img = image.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img).strip()
    return text

def extract_data(page_image, boxes, account_number, account_name):
    """
    Extracts data from pages 1 and 2 regarding discretion/non-discretion.
    
    Args:
        page_image (PIL.Image): The image of the PDF page
        boxes (list): List of bounding boxes
        account_number (str): Account number from precondition check
        account_name (str): Account name from precondition check
        
    Returns:
        dict: Extracted data including account details and discretion status
    """
    extracted_data = {
        "Account Number": account_number,
        "Account Name": account_name,
        "Discretion Status": None,
        "Account Type": None
    }

    for box in boxes:
        x, y, width, height = box
        text = extract_text_from_bbox(page_image, box)
        
        if box == (100, 150, 200, 50):  # Adjust coordinates as needed
            extracted_data["Discretion Status"] = text.strip()
        elif box == (100, 220, 200, 50):  # Adjust coordinates as needed
            extracted_data["Account Type"] = text.strip()

    return extracted_data

# Define bounding boxes for the script
bounding_boxes = {
    "page_number": 1,  # Update if needed for page 2
    "boxes": [
        (100, 150, 200, 50),  # Discretion Status
        (100, 220, 200, 50),  # Account Type
    ]
}

def main(input_directory, output_directory):
    """
    Main function to process all PDFs in the input directory.

    Args:
        input_directory (str): The directory containing PDF files.
        output_directory (str): The directory to save the results.
    """
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            try:
                process_pdf(pdf_path, output_directory)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python detect_signature_page1,2.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)





