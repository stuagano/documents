#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
import pandas as pd
from PIL import Image, ImageDraw

def has_docusign_signature(pdf_path):
    """
    Checks if a PDF page has a DocuSign signature.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        bool: True if a DocuSign signature is likely present, False otherwise.
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        
        for page_image in images:
            # Use OCR to extract text from the page
            text = pytesseract.image_to_string(page_image)
            if "DocuSign" in text:
                return True
        return False
        
    except Exception as e:
        print(f"Error checking for DocuSign signature: {e}")
        return False

def process_pdf(pdf_path, output_directory):
    """
    Processes a single PDF to detect DocuSign signatures.

    Args:
        pdf_path (str): The path to the PDF file.
        output_directory (str): The directory to save the results.
    """
    signature_present = has_docusign_signature(pdf_path)
    result = {
        "PDF": os.path.basename(pdf_path),
        "DocuSign Signature": signature_present
    }
    
    result_file = os.path.join(output_directory, 'signature_results.csv')
    df = pd.DataFrame([result])
    
    if not os.path.exists(result_file):
        df.to_csv(result_file, index=False)
    else:
        df.to_csv(result_file, mode='a', header=False, index=False)
    
    print(f"Processed: {pdf_path} - DocuSign Signature: {signature_present}")

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




