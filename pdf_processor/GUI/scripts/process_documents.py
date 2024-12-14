import csv
import argparse
import json
import os
import logging
import datetime

from PIL import Image, ImageDraw
import pytesseract

from pdf_processor.utils import (get_pdf_images,
                                  remove_gridlines_from_image,
                                  run_precondition_checks)
from pdf_processor.utils.base_utils import display_image_with_boxes


def read_config(config_path):
    """Reads the configuration file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def extract_text_from_bbox(image, bbox):
    """Extracts text from a bounding box in an image using OCR."""
    x1, y1, x2, y2 = bbox
    cropped_image = image.crop((x1, y1, x2, y2))
    text = pytesseract.image_to_string(cropped_image)
    return text


def process_pdf(pdf_path, config, investment_experience_type):
    """Processes a single PDF file and extracts information."""
    extracted_data = {}
    images = get_pdf_images(pdf_path)

    try:
        # Process 'Investment Experience' field based on type
        if investment_experience_type == "radio":
            field_name = "Investment Experience"
            field_config = config.get(field_name)
            if field_config:
                page_number = field_config['page']
                bbox = field_config.get('investment_experience_radio_bbox', field_config['bbox'])  # Fallback to 'bbox' if 'investment_experience_radio_bbox' is not present
                if 1 <= page_number <= len(images):
                    text = extract_text_from_bbox(images[page_number - 1], bbox)
                    extracted_data[field_name] = text
                    extracted_data["investment_experience_field_type"] = "radio"  # Indicate radio button type
                else:
                    print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
            else:
                print(f"Field configuration not found for: {field_name} skipping.")

        elif investment_experience_type == "text":
            field_name = "Investment Experience"
            field_config = config.get(field_name)
            if field_config:
                page_number = field_config['page']
                bbox = field_config.get('investment_experience_text_bbox', field_config['bbox'])  # Fallback to 'bbox' if 'investment_experience_text_bbox' is not present
                if 1 <= page_number <= len(images):
                    text = extract_text_from_bbox(images[page_number - 1], bbox)
                    extracted_data[field_name] = text
                    extracted_data["investment_experience_field_type"] = "text"  # Indicate text box type
                else:
                    print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
            else:
                print(f"Field configuration not found for: {field_name} skipping.")

        # Process other fields in the order defined in config
        for field_name, field_config_list in config.items():
            if field_name != "Investment Experience" and field_name != "investment_experience_type":
                # Check if it's a list of configs (for multiple methods)
                if isinstance(field_config_list, list):
                    for field_config in field_config_list:
                        page_number = field_config['page']
                        bbox = field_config['bbox']
                        if 1 <= page_number <= len(images):
                            # Remove gridlines before extraction
                            image_without_gridlines = remove_gridlines_from_image(images[page_number - 1])
                            text = extract_text_from_bbox(image_without_gridlines, bbox)
                            extracted_data[field_name] = text
                        else:
                            print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
                else:  # If not a list, treat as a single config
                    page_number = field_config_list['page']
                    bbox = field_config_list['bbox']
                    if 1 <= page_number <= len(images):
                        text = extract_text_from_bbox(images[page_number - 1], bbox)
                        extracted_data[field_name] = text
                    else:
                        print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")

    except Exception as e:
        # Log the error
        with open(os.path.join(output_dir, 'error.log'), 'a') as error_log:
            error_log.write(f"Error processing {pdf_path}: {str(e)}\n")
        print(f"Error processing {pdf_path}: {str(e)}")
        return None


    return extracted_data

def write_to_csv(data, output_path):
    """Writes extracted data to a CSV file, handling potential errors.
    Logs errors to a file named 'csv_errors.log'.
    """
    # Configure logging
    logging.basicConfig(filename='csv_errors.log', level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        if data:  # Check if data is not empty
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data.keys()  # Get the keys from the first data item
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()  # Write the field names as the header
                writer.writerow(data)  # Write the data to the CSV
        else:
            logging.error(f"No data to write for {output_path}") 
    except Exception as e:
        logging.error(f"Error writing to CSV at {output_path}: {e}") 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract data from PDF files.')
    parser.add_argument('input_dir', help='Path to the input directory containing PDF files.')
    parser.add_argument('output_dir', help='Path to the output directory for CSV files.')
    parser.add_argument('config_path', help='Path to the config.json file.')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    config_path = args.config_path

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        config = read_config(config_path)  # Read the configuration file
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        precondition_results = run_precondition_checks(input_dir, pdf_files, config)  # Run precondition checks

        # Display precondition results
        for result in precondition_results:
            if result['failed_checks'] > 0:
                print(f"Precondition checks failed for {result['filename']}: {result.get('failed_checks', 0)} checks failed.")

        # Prompt user if there were any failures
        if any(result.get('failed_checks', 0) > 0 for result in precondition_results):
            proceed = input("Precondition checks had warnings for some documents. Do you want to continue? (y/n): ")
            if proceed.lower() != 'y':
                print("Processing aborted.")
                exit()

        # Process PDFs if preconditions pass or user chooses to continue
        investment_experience_type = config.get("investment_experience_type")

        if investment_experience_type is None:
            while True:
                investment_experience_type = input("Enter the type of 'Investment Experience' field (radio/text): ").lower()
                if investment_experience_type in ("radio", "text"):
                    break
                else:
                    print("Invalid input. Please enter 'radio' or 'text'.")

        for filename in pdf_files:
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing: {pdf_path} (Investment Experience: {investment_experience_type})")
            extracted_data = process_pdf(pdf_path, config, investment_experience_type)

            if extracted_data:
                output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.csv')
                write_to_csv(extracted_data, output_file)
            else:
                print(f"Failed to process {pdf_path}. Skipping...")

    except Exception as e:
        print(f"An error occurred: {e}")

    print("Processing complete.")