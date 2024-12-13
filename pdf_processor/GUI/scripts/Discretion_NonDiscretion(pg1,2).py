#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
from PyPDF2 import PdfFileReader

from pdf_processor.utils import extract_text_from_bbox, display_image_with_boxes, precondition_check, check_for_signature

def has_docusign_signature(pdf_path):
    """
    Checks if a PDF page has a DocuSign signature.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        bool: True if a DocuSign signature is likely present, False otherwise.
    """
    try:
        print(f"Checking for DocuSign signature in PDF: {pdf_path}")
        pdf_document = PdfFileReader(open(pdf_path, 'rb'))
        for page_num in range(pdf_document.getNumPages()):
            page = pdf_document.getPage(page_num)
            text = page.extract_text()
            if "DocuSign" in text:
                print(f"DocuSign signature found on page {page_num + 1}")
                return True
        print("No DocuSign signature found in the PDF.")
        return False
    except Exception as e:
        print(f"Error checking DocuSign signature: {e}")
        return False

def write_results_to_csv(file_path, result):
    import csv
    header = ["PDF", "Account Number", "Account Name", "Initials Found", "Pages with Initials"]
    file_exists = os.path.isfile(file_path)
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
        print(f"Results successfully written to CSV: {file_path}")
    except Exception as e:
        print(f"Failed to write results to CSV: {e}")

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
    print("Starting data extraction...")
    extracted_data = {
        "Account Number": account_number,
        "Account Name": account_name,
        "Discretion Status": None,
        "Account Type": None
    }

    for box in boxes:
        x, y, width, height = box
        print(f"Processing box: {box}")
        text = extract_text_from_bbox(page_image, box)
        print(f"Extracted Text: {text}")

        if box == (100, 150, 200, 50):  # Discretion Status
            extracted_data["Discretion Status"] = text.strip()
            print(f"Discretion Status set to: {extracted_data['Discretion Status']}")
        
        elif box == (100, 220, 200, 50):  # Account Type
            extracted_data["Account Type"] = text.strip()
            print(f"Account Type set to: {extracted_data['Account Type']}")
        
        # Add other conditional extractions as needed
        else:
            print(f"No matching condition for box: {box}")

    print(f"Final Extracted Data: {extracted_data}")
    return extracted_data

def process_pdf(pdf_path, output_directory):
    """
    Processes a PDF to extract account info and check for initials.

    Args:
        pdf_path (str): The path to the PDF file.
        output_directory (str): The directory to save the results.
    """
    print(f"Processing PDF: {pdf_path}")
    print(f"Output Directory: {output_directory}")

    try:
        # Open the PDF document
        pdf_file = open(pdf_path, 'rb')
        pdf_document = PdfFileReader(pdf_file)
        print("PDF document opened successfully.")

        # Check for DocuSign signature
        if not has_docusign_signature(pdf_path):
            print("DocuSign signature not found. Proceeding with extraction.")
        else:
            print("DocuSign signature found. Proceeding with extraction.")

        # Define bounding boxes in the format (x, y, width, height)
        account_number_bbox = (450, 50, 150, 30)  # Top-right of page 1
        account_name_bbox = (50, 50, 300, 30)     # Adjust coordinates as needed
        boxes = [account_number_bbox, account_name_bbox]
        labels = ["Account Number", "Account Name"]

        # Convert page 1 to image
        page_number = 1
        if page_number > pdf_document.getNumPages():
            print(f"Page {page_number} does not exist in the PDF.")
            return

        page = pdf_document.getPage(page_number - 1)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        print(f"Converted page {page_number} to image.")

        # Display image with bounding boxes and ask for confirmation
        display_image_with_boxes(img.copy(), boxes, labels)
        print("Displayed image with bounding boxes for user confirmation.")

        # Ask for user confirmation
        user_input = input("Are the bounding boxes correctly placed? (y/n): ")
        if user_input.lower() != 'y':
            print("User chose to adjust bounding boxes. Exiting extraction process.")
            return
        print("User confirmed bounding boxes. Proceeding with extraction.")

        # Run precondition check
        print("Running precondition check...")
        images = convert_from_path(pdf_path, dpi=300, first_page=page_number, last_page=page_number)
        precondition_results = precondition_check(images, parent=None)  # Set parent if using GUI
        print(f"Precondition Results: {precondition_results}")

        # Retrieve Account Number and Account Name
        account_number = precondition_results.get("Account Number", "Not Found")
        account_name = precondition_results.get("Account Name", "Not Found")
        print(f"Account Number: {account_number}")
        print(f"Account Name: {account_name}")

        # Proceed with data extraction
        extracted_data = extract_data(img, boxes, account_number, account_name)
        print(f"Extracted Data: {extracted_data}")

        # Save extracted data
        output_file = os.path.join(
            output_directory,
            f"{os.path.splitext(os.path.basename(pdf_path))[0]}_discretion_nondiscretion_output.json"
        )
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=4)
            print(f"Extracted data saved to {output_file}")
        except Exception as e:
            print(f"Failed to save extracted data: {e}")

        # Compile results for CSV
        initials_info = {
            "total_initials": 0,  # Placeholder, implement actual logic
            "pages_with_initials": []
        }
        result = {
            "PDF": os.path.basename(pdf_path),
            "Account Number": account_number,
            "Account Name": account_name,
            "Initials Found": initials_info["total_initials"],
            "Pages with Initials": initials_info["pages_with_initials"]
        }
        print(f"Compiled Result for CSV: {result}")

        # Save results to CSV
        result_file = os.path.join(output_directory, 'discretion_nondiscretion_results.csv')
        write_results_to_csv(result_file, result)

    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")

def main(input_directory, output_directory):
    """
    Main function to process all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save extracted data and results.
    """
    print(f"Input Directory: {input_directory}")
    print(f"Output Directory: {output_directory}")

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created output directory: {output_directory}")
        except Exception as e:
            print(f"Failed to create output directory: {e}")
            return

    # Iterate through all PDF files in the input directory
    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Found PDF: {pdf_path}")
            process_pdf(pdf_path, output_directory)
        else:
            print(f"Skipped non-PDF file: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Discretion_NonDiscretion(pg1,2).py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)