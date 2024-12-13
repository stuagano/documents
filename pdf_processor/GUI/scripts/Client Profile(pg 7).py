import os
import sys
import json
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

from pdf_processor.utils import (
    extract_text_from_bbox,
    check_for_signature,
    precondition_check,
    display_image_with_boxes
)

def process_pdf(pdf_path, output_directory):
    """Process a single PDF file."""
    print(f"Processing PDF: {pdf_path}")
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        if not images:
            print("No pages found in PDF")
            return
            
        # Run precondition check
        print("Running precondition check...")
        precondition_results = precondition_check(images)
        print(f"Precondition results: {precondition_results}")
        
        # Extract data from page 7
        page_image = images[6]  # 0-based index for page 7
        extracted_data = extract_data(page_image, precondition_results)
        print(f"Extracted data: {extracted_data}")
        
        # Save results
        output_file = os.path.join(
            output_directory,
            f"{os.path.splitext(os.path.basename(pdf_path))[0]}_client_profile_output.json"
        )
        with open(output_file, 'w') as f:
            json.dump(extracted_data, f, indent=4)
        print(f"Results saved to: {output_file}")
            
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")

def extract_data(page_image, precondition_results):
    """Extract data from page 7 of client profile."""
    print("Extracting data from page 7...")
    extracted_data = {
        "Account Number": precondition_results.get("Account Number"),
        "Account Name": precondition_results.get("Account Name"),
        # Add other fields as needed
    }
    return extracted_data

def main(input_directory, output_directory):
    """Process all PDFs in input directory."""
    print(f"Starting processing from {input_directory}")
    print(f"Saving results to {output_directory}")
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")
    
    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            print(f"\nProcessing: {filename}")
            process_pdf(pdf_path, output_directory)
        else:
            print(f"Skipping non-PDF file: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 'Client Profile(pg 7).py' <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)