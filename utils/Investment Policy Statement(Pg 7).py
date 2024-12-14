# PAGE7.PY

import os
import sys
import cv2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import numpy as np
import re
import json

# Define bounding boxes and the page number
bounding_boxes = {
    "page_number": 7,
    "boxes": [
        (100, 150, 400, 200),   # Investment Experience
        (600, 150, 400, 200),   # Client Profile
        (100, 400, 900, 300),   # Account Profile
        # Add other boxes as needed
    ]
}

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

def remove_grid_lines(image, lines):
    """Removes detected grid lines from the image."""
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(np.array(image), (x1, y1), (x2, y2), (255, 255, 255), 2) 
    return image




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

def extract_investment_experience(text):
    """Extracts Investment Experience from text."""
    # Implement your extraction logic here
    return text  # Placeholder

def extract_client_profile(text):
    """Extracts Client Profile from text."""
    # Implement your extraction logic here
    return text  # Placeholder

def extract_account_profile(text):
    """Extracts Account Profile from text."""
    # Implement your extraction logic here
    return text  # Placeholder

def extract_data(page_image, boxes):
    """
    Extracts data from the specified bounding boxes on the given page image.

    Args:
        page_image (PIL.Image.Image): The image of the PDF page.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).

    Returns:
        dict: Extracted data.
    """
    extracted_data = {}
    for box in boxes:
        x, y, width, height = box
        cropped_img = page_image.crop((x, y, x + width, y + height))

        # Detect and remove grid lines
        grid_lines = detect_grid_lines(cropped_img)
        cropped_img = remove_grid_lines(cropped_img, grid_lines)
        text = pytesseract.image_to_string(cropped_img).strip()  

        if box == (100, 150, 400, 200):
            extracted_data["Investment Experience"] = extract_investment_experience(text)
        elif box == (600, 150, 400, 200):
            extracted_data["Client Profile"] = extract_client_profile(text)
        elif box == (100, 400, 900, 300):
            extracted_data["Account Profile"] = extract_account_profile(text)
        # Add other conditional extractions as needed
    return extracted_data

def main(pdf_path, output_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)
    page_number = bounding_boxes["page_number"]
    if page_number > len(images):
        print(f"Page {page_number} does not exist in the PDF.")
        return
    
    page_image = images[page_number - 1].convert('RGB')
    
    # Define bounding boxes
    boxes = bounding_boxes["boxes"]
    
    # Display image with bounding boxes
    display_image_with_boxes(page_image.copy(), {
        "Investment Experience": boxes[0],
        "Client Profile": boxes[1],
        "Account Profile": boxes[2]
    })
    
    # Extract and process sections
    extracted_data = extract_data(page_image, boxes)
    
    # Save extracted data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4)
    
    print(f"Extracted data saved to {output_path}")

if __name__ == '__main__':
    pdf_path = 'path_to_pdf.pdf'
    output_path = 'extracted_data_page7.json'
    main(pdf_path, output_path)