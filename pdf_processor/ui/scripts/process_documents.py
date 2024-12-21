import csv
import argparse
import json
import os
import logging
import datetime
import pandas as pd
import json
import shlex
import jsonschema

from PIL import Image, ImageDraw
import pytesseract

from pdf_processor.utils import (get_pdf_images,
                                  remove_gridlines_from_image,
                                  run_precondition_checks, DESCRIPTION, POST_PROCESSING_LOGIC)
from pdf_processor.ui.scripts.config_constants import PAGE_NUMBER, BOXES, FIELD_NAME, COORDINATES
from pdf_processor.utils.base_utils import display_image_with_boxes
from pdf_processor.pdf_processing import process_pdf, extract_text_from_bbox, validate_config, read_config





def display_dataframe_head(df):
    """Prints the first 5 rows of a Pandas DataFrame to the console."""
    print(df.head())


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
                df = pd.DataFrame([data])  # Create DataFrame
                display_dataframe_head(df)  # Display first 5 rows
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

    input_dir = os.path.abspath(args.input_dir)  # Sanitize input_dir
    output_dir = os.path.abspath(args.output_dir)  # Sanitize output_dir
    config_path = os.path.abspath(args.config_path)  # Sanitize config_path

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    
    validate_config(config_path) # Validate the configuration file
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
        pdf_path = os.path.abspath(os.path.join(input_dir, filename)) # Sanitize pdf_path
        print(f"Processing: {pdf_path} (Investment Experience: {investment_experience_type})")
        extracted_data = process_pdf(pdf_path, config, investment_experience_type)

        if extracted_data:
            output_file = os.path.abspath(os.path.join(output_dir, os.path.splitext(filename)[0] + '.csv'))
            write_to_csv(extracted_data, output_file)
        else:
            print(f"Failed to process {pdf_path}. Skipping..")
    print("Processing complete.")