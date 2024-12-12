# PDF_TextExtractor.py
#!/usr/bin/env python
# coding: utf-8

import os
import sys
import cv2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import re
import json

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

def process_pdf(pdf_path, output_directory):
    """
    Processes a single PDF to extract text and save it.

    Args:
        pdf_path (str): Path to the PDF file.
        output_directory (str): Directory to save the extracted text.
    """
    text = extract_text_from_pdf(pdf_path)
    if text:
        output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
        output_path = os.path.join(output_directory, output_filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Extracted text saved to {output_path}")
        except Exception as e:
            print(f"Error saving text for {pdf_path}: {e}")

def extract_data(input_directory, output_directory):
    """
    Extracts text data from all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted text files.
    """
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing file: {filename}")
            process_pdf(pdf_path, output_directory)

def detect_grid_lines(image):
    """
    Detects grid lines in the image and visualizes them, filtering out short lines.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                   cv2.ADAPTIVE_THRESH_MEAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=4)
    
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    grid_lines = cv2.bitwise_or(vertical_lines, horizontal_lines)

    lines = cv2.HoughLinesP(grid_lines, 1, np.pi/180, 100, 
                            minLineLength=100, maxLineGap=10)

    filtered_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if line_length > 100:
                filtered_lines.append(line)

    return filtered_lines

def display_image_with_boxes(image, boxes, title="Confirm Bounding Boxes"):
    """
    Displays the image with bounding boxes for user confirmation.
    
    Args:
        image (PIL.Image.Image): The image to display.
        boxes (dict): Dictionary of bounding boxes with section names as keys.
    """
    draw = ImageDraw.Draw(image)
    for section, box in boxes.items():
        x, y, width, height = box
        draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=2)
        draw.text((x, y - 15), section, fill="red")  # Label the sections

    image.show(title=title)

def extract_text_from_box(image, box):
    """
    Crops the image to the bounding box and extracts text using OCR.
    
    Args:
        image (PIL.Image.Image): The original image.
        box (tuple): Bounding box coordinates (x, y, width, height).
    
    Returns:
        str: Extracted text.
    """
    x, y, width, height = box
    cropped_img = image.crop((x, y, x + width, y + height))
    text = pytesseract.image_to_string(cropped_img)
    return text.strip()

def extract_investment_data(text):
    """
    Extracts investment experience data from the extracted text.
    
    Args:
        text (str): The extracted text from the PDF.
    
    Returns:
        dict: Extracted investment data.
    """
    patterns = {
        "Investment Experience": r"Investment Experience:\s*(.+)",
        "Years of Experience": r"Years of Experience:\s*(\d+)",
        "Primary Investments": r"Primary Investments:\s*(.+)"
    }
    
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        data[key] = match.group(1).strip() if match else None
    return data

def extract_client_profile(text):
    """
    Extracts client profile data from the extracted text.
    
    Args:
        text (str): The extracted text from the PDF.
    
    Returns:
        dict: Extracted client profile data.
    """
    patterns = {
        "Client Name": r"Client Name:\s*(.+)",
        "Client Age": r"Age:\s*(\d+)",
        "Client Address": r"Address:\s*(.+)"
    }
    
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        data[key] = match.group(1).strip() if match else None
    return data

def extract_account_profile(text):
    """
    Extracts account profile data from the extracted text.
    
    Args:
        text (str): The extracted text from the PDF.
    
    Returns:
        dict: Extracted account profile data.
    """
    patterns = {
        "Account Number": r"Account Number:\s*(\d+)",
        "Account Type": r"Account Type:\s*(.+)"
    }
    
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        data[key] = match.group(1).strip() if match else None
    return data

def main(input_directory, output_directory):
    """
    Main function to process all PDFs in the input directory.

    Args:
        input_directory (str): Directory containing PDF files.
        output_directory (str): Directory to save the extracted text files.
    """
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)
    extract_data(input_directory, output_directory)

def main_page7(pdf_path, output_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)
    page_number = 7
    if page_number > len(images):
        print(f"Page {page_number} does not exist in the PDF.")
        return
    
    page_image = images[page_number - 1].convert('RGB')
    
    # Define bounding boxes
    bounding_boxes = {
        "Investment Experience": (100, 150, 400, 200),  # (x, y, width, height)
        "Client Profile": (600, 150, 400, 200),
        "Account Profile": (100, 400, 900, 300)
    }
    
    # Display image with bounding boxes
    display_image_with_boxes(page_image.copy(), bounding_boxes)
    
    # Extract and process sections
    investment_text = extract_text_from_box(page_image, bounding_boxes["Investment Experience"])
    client_text = extract_text_from_box(page_image, bounding_boxes["Client Profile"])
    account_text = extract_text_from_box(page_image, bounding_boxes["Account Profile"])
    
    extracted_data = {}
    extracted_data.update(extract_investment_data(investment_text))
    extracted_data.update(extract_client_profile(client_text))
    extracted_data.update(extract_account_profile(account_text))
    
    # Save extracted data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4)
    
    print(f"Extracted data saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python PDF_TextExtractor.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)




