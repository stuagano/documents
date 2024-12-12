# Page7Extractor.py
#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import pandas as pd

def extract_fields_from_text(text):
    """
    Extracts specific fields from the provided text.
    
    Args:
        text (str): The extracted text from the PDF.
    
    Returns:
        dict: A dictionary containing the extracted fields.
    """
    profile_data = {}
    lines = text.split('\n')
    try:
        # Locate the starting index after "Owner 1" line
        start_index = next(i for i, line in enumerate(lines) if "Owner 1" in line)
        current_index = start_index + 1  # Start after Owner 1 line

        for field in ["Annual Income", "Net Worth", "Liquid Net Worth", "Tax Bracket"]:
            while current_index < len(lines):
                line = lines[current_index].strip()
                if field in line:
                    value_match = re.search(rf"{field}:\s*(.*)", line)
                    profile_data[field] = value_match.group(1).strip() if value_match else None
                    current_index += 1  # Move to next line to prevent infinite loop
                    break
                elif any(keyword in line for keyword in ["Annual Income", "Net Worth", "Liquid Net Worth", "Tax Bracket"]):
                    break  # Stop if you encounter a different field
                elif re.search(r"\d+", line):  # Stop search if numerical data
                    break
                else:
                    current_index += 1
            else:
                profile_data[field] = None  # If field is not found
    except StopIteration:
        print("DEBUG: 'Owner 1' line not found in text.")

    return profile_data

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using Tesseract OCR.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: The extracted text.
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=300)
        
        extracted_text = ""
        for img in images:
            text = pytesseract.image_to_string(img)
            extracted_text += text + "\n"
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def process_pdf(pdf_path):
    """
    Processes a single PDF to extract profile information.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        dict: Extracted profile data.
    """
    text = extract_text_from_pdf(pdf_path)
    if text:
        profile_data = extract_fields_from_text(text)
        profile_data["PDF"] = os.path.basename(pdf_path)
        return profile_data
    else:
        return {"PDF": os.path.basename(pdf_path), "Annual Income": None, "Net Worth": None, "Liquid Net Worth": None, "Tax Bracket": None}

def extract_data(input_directory, output_directory):
    """
    Extracts profile data from all PDFs in the input directory and saves to CSV.
    
    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted data.
    """
    data = []
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing file: {filename}")
            profile_data = process_pdf(pdf_path)
            data.append(profile_data)
    
    # Save the extracted data to a CSV file
    output_file = os.path.join(output_directory, 'client_profiles.csv')
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Data extracted and saved to {output_file}")

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
        print("Usage: python Page7Extractor.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)
