import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

def display_image_with_boxes(pdf_path, page_number, boxes):
    # Implementation for displaying image with boxes
    pass  # Replace with actual implementation

def extract_account_number(text):
    """Extracts account number in the format GCWXXXXXX from text."""
    match = re.search(r"GCW\d{6}", text)
    if match:
        return match.group(0)
    return None

def extract_account_name(text):
    """Extracts the account name following the specified pattern."""
    match = re.search(r"This agreement is entered into by and between\s+(.+)", text)
    if match:
        return match.group(1)
    return None

def process_pdf(pdf_path, output_directory):
    page_number = 10  # Replace with the desired page number

    # Define the bounding boxes you want to visualize
    boxes = [
        (450, 750, 400, 200),  # Example box for "Annual Income 1"
        (450, 1075, 1600, 300), # Example box for "Annual Income 2"
        # Add other boxes here...
    ]

    display_image_with_boxes(pdf_path, page_number, boxes)

    # Example text extraction (replace with actual text extraction logic)
    extracted_text = "This agreement is entered into by and between GCW123456 and another party."

    account_number = extract_account_number(extracted_text)
    account_name = extract_account_name(extracted_text)

    # Save the extracted information to the output directory
    with open(os.path.join(output_directory, 'extracted_info.txt'), 'a') as f:
        f.write(f"PDF: {os.path.basename(pdf_path)}\n")
        f.write(f"Account Number: {account_number}\n")
        f.write(f"Account Name: {account_name}\n\n")

def main(input_directory, output_directory):
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing: {pdf_path}")
            try:
                process_pdf(pdf_path, output_directory)
                print(f"Successfully processed: {filename}\n")
            except Exception as e:
                print(f"Error processing {filename}: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Account_Number.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)