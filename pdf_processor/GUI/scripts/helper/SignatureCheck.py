# DocuSignSignatureChecker.py
#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import io
import cv2
import numpy as np
import pytesseract
import pandas as pd
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import subprocess

def has_docusign_signature(pdf_path, template_path="IAA_Yonamine_J_Roth_Discretion.png"):
    """
    Checks if a PDF contains a DocuSign signature by matching a template image.

    Args:
        pdf_path (str): The path to the PDF file.
        template_path (str): The path to the template image for signature detection.

    Returns:
        bool: True if a DocuSign signature is detected, False otherwise.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pixmap = page.get_pixmap()
            img_data = pixmap.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Load the template image in grayscale
            template = cv2.imread(template_path, 0)
            if template is None:
                print(f"Template image not found at path: {template_path}")
                return False

            # Check if the template is larger than the source image
            if template.shape[0] > opencv_img.shape[0] or template.shape[1] > opencv_img.shape[1]:
                # Calculate scaling factor
                scale_factor = min(
                    opencv_img.shape[0] / template.shape[0],
                    opencv_img.shape[1] / template.shape[1]
                ) * 0.9  # Scale down slightly to ensure it fits

                # Resize the template
                new_width = int(template.shape[1] * scale_factor)
                new_height = int(template.shape[0] * scale_factor)
                template = cv2.resize(template, (new_width, new_height))

            # Convert source image to grayscale
            opencv_img_gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)

            # Ensure the source image has the same depth as the template
            if template.dtype == np.uint8:
                opencv_img_gray = opencv_img_gray.astype(np.uint8)
            elif template.dtype == np.float32:
                opencv_img_gray = opencv_img_gray.astype(np.float32)

            # Perform template matching
            res = cv2.matchTemplate(opencv_img_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)

            if len(loc[0]) > 0:
                return True

        return False

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def clean_and_extract_entities(text):
    """
    Cleans up text and extracts entities using spaCy.

    Args:
        text (str): The input text.

    Returns:
        list: A list of extracted entities.
    """
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")  # Load a spaCy model

        # Clean up the text
        cleaned_text = text.strip()

        doc = nlp(cleaned_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities
    except Exception as e:
        print(f"Error processing text for entities: {e}")
        return None

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
            # Convert PIL Image to RGB mode (required by pytesseract)
            img = img.convert('RGB')
            text = pytesseract.image_to_string(img, config='--oem 1 --psm 11')
            extracted_text += text + "\n"  # Add a newline after each page

        return extracted_text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def extract_account_number(text):
    """
    Extracts account number in the format GCWXXXXXX from text.

    Args:
        text (str): The extracted text.

    Returns:
        str or None: The account number if found, else None.
    """
    match = re.search(r"GCW\d{6}", text)
    if match:
        return match.group(0)
    return None 

def extract_account_name(text):
    """
    Extracts the underlined account name after "This agreement...".

    Args:
        text (str): The extracted text.

    Returns:
        str or None: The account name if found and underlined, else None.
    """
    match = re.search(r"This agreement is entered into by and between\s+(.+)", text)
    if match:
        account_name = match.group(1).strip()
        # Assuming the account name is always underlined
        if account_name.startswith("_") and account_name.endswith("_"):
            return account_name[1:-1]  # Remove underlines
    return None

def extract_entities(text):
    """
    Extracts entities from text.

    Args:
        text (str): The extracted text.

    Returns:
        list or None: A list of entities if extraction is successful, else None.
    """
    return clean_and_extract_entities(text)

def process_pdf(pdf_path, template_path):
    """
    Processes a single PDF to check for DocuSign signature and extract relevant data.

    Args:
        pdf_path (str): Path to the PDF file.
        template_path (str): Path to the signature template image.

    Returns:
        dict: Extracted data including signature presence, account number, and account name.
    """
    try:
        signature_present = has_docusign_signature(pdf_path, template_path)
        extracted_text = extract_text_from_pdf(pdf_path)
        entities = extract_entities(extracted_text)

        account_number = extract_account_number(extracted_text)
        account_name = extract_account_name(extracted_text)

        data = {
            "PDF": os.path.basename(pdf_path),
            "DocuSign Signature": "Y" if signature_present else "N",
            "Account Number": account_number,
            "Account Name": account_name,
            "Entities": entities
        }

        return data

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return {
            "PDF": os.path.basename(pdf_path),
            "DocuSign Signature": "Error",
            "Account Number": None,
            "Account Name": None,
            "Entities": None
        }

def process_pdfs_in_directory(input_directory, output_directory, template_path="IAA_Yonamine_J_Roth_Discretion.png", batch_size=3):
    """
    Processes PDF files in batches, extracts data, and stores in CSV files.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted data.
        template_path (str): Path to the signature template image.
        batch_size (int): Number of PDFs to process in each batch.
    """
    all_data = []
    pdf_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.pdf')]

    for i in range(0, len(pdf_files), batch_size):
        batch_files = pdf_files[i: i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of {len(pdf_files) // batch_size + (1 if len(pdf_files) % batch_size else 0)}")

        for filename in batch_files:
            pdf_path = os.path.join(input_directory, filename)

            try:
                data = process_pdf(pdf_path, template_path)
                all_data.append(data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
            continue  # Continue with the next PDF

        # Create DataFrame for the current batch and save to CSV
        df_batch = pd.DataFrame(all_data)
        batch_output_filename = f"batch_{i // batch_size + 1}.csv"
        batch_output_path = os.path.join(output_directory, batch_output_filename)
        df_batch.to_csv(batch_output_path, index=False)
        print(f"Batch data written to: {batch_output_path}\n")

    # Create a consolidated DataFrame after processing all PDFs
    df_all = pd.DataFrame(all_data)
    all_output_path = os.path.join(output_directory, "all_pdf_data.csv")
    df_all.to_csv(all_output_path, index=False)
    print(f"All data consolidated and saved to: {all_output_path}")

def main(input_directory, output_directory, template_path="IAA_Yonamine_J_Roth_Discretion.png", batch_size=3):
    """
    Main function to process all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted data.
        template_path (str): Path to the signature template image.
        batch_size (int): Number of PDFs to process in each batch.
    """
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)

    if not os.path.isfile(template_path):
        print(f"Template image not found at path: {template_path}")
        sys.exit(1)

    process_pdfs_in_directory(input_directory, output_directory, template_path, batch_size)

if __name__ == "__main__":
    if len(sys.argv) not in [3, 5]:
        print("Usage: python DocuSignSignatureChecker.py <input_directory> <output_directory> [<template_path> <batch_size>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    template_img_path = sys.argv[3] if len(sys.argv) == 5 else "IAA_Yonamine_J_Roth_Discretion.png"
    batch_size_value = int(sys.argv[4]) if len(sys.argv) == 5 else 3

    main(input_dir, output_dir, template_img_path, batch_size_value)