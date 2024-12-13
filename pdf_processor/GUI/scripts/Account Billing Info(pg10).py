#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import pandas as pd

def extract_account_number(text):
    """Extracts account number in the format GCWXXXXXX from text."""
    match = re.search(r"GCW\d{6}", text)
    if match:
        return match.group(0)
    return None 

def extract_account_name(text):
    """Extracts the underlined account name after "This agreement..."."""
    match = re.search(r"This agreement is entered into by and between\s+(.+)", text)
    if match:
        account_name = match.group(1).strip()
        # Assuming the account name is always underlined
        if account_name.startswith("_") and account_name.endswith("_"):
            return account_name[1:-1]  # Remove underlines
    return None  

def extract_fee_page_10(pdf_path):
    """Extracts text to the right of "Fee to be Charged:" on page 10."""
    try:
        images = convert_from_path(pdf_path, dpi=300, first_page=10, last_page=10)
        if images:
            img = images[0].convert('RGB')

            # Define ROI for the area to the right of "Fee to be Charged:"
            x, y, width, height = 450, 750, 400, 200  # Adjust these coordinates
            cropped_img = img.crop((x, y, x + width, y + height))

            # Extract text from the ROI using OCR
            extracted_text = pytesseract.image_to_string(cropped_img).strip()
            return extracted_text
    except Exception as e:
        print(f"Error extracting fee from page 10: {e}")
        return "INCOMPLETE"

def extract_additional_instructions_page_10(pdf_path):
    """Extracts text below "Additional Instructions" on page 10."""
    try:
        images = convert_from_path(pdf_path, dpi=300, first_page=10, last_page=10)
        if images:
            img = images[0].convert('RGB')

            # Define ROI for the area below "Additional Instructions"
            x, y, width, height = 100, 950, 800, 200  # Adjust these coordinates
            cropped_img = img.crop((x, y, x + width, y + height))

            # Extract text from the ROI using OCR
            extracted_text = pytesseract.image_to_string(cropped_img).strip()
            return extracted_text
    except Exception as e:
        print(f"Error extracting additional instructions from page 10: {e}")
        return "INCOMPLETE"

def process_pdf(pdf_path, output_directory):
    """
    Processes a single PDF to extract account information and fees from page 10.

    Args:
        pdf_path (str): Path to the PDF file.
        output_directory (str): Directory to save the extracted data.
    """
    try:
        images = convert_from_path(pdf_path, dpi=300, first_page=10, last_page=10)
        if images:
            img = images[0].convert('RGB')
            text = pytesseract.image_to_string(img)
            
            account_number = extract_account_number(text)
            account_name = extract_account_name(text)
            fee = extract_fee_page_10(pdf_path)
            additional_instructions = extract_additional_instructions_page_10(pdf_path)

            data = {
                "PDF": os.path.basename(pdf_path),
                "Account Number": account_number,
                "Account Name": account_name,
                "Fee to be Charged": fee,
                "Additional Instructions": additional_instructions
            }

            output_file = os.path.join(output_directory, 'page10_extracted_data.csv')
            df = pd.DataFrame([data])

            if not os.path.exists(output_file):
                df.to_csv(output_file, index=False)
            else:
                df.to_csv(output_file, mode='a', header=False, index=False)

            print(f"Extracted data saved to {output_file}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

def extract_data(input_directory, output_directory):
    """
    Extracts data from all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted data.
    """
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing file: {filename}")
            process_pdf(pdf_path, output_directory)

def main(input_directory, output_directory):
    """
    Main function to process all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted data.
    """
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)
    extract_data(input_directory, output_directory)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Page10Extractor.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)




