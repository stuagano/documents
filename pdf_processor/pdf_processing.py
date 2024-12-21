import json
import os
import jsonschema
from PIL import Image
import pytesseract
from pdf_processor.utils import get_pdf_images, remove_gridlines_from_image
from pdf_processor.ui.scripts.config_constants import PAGE_NUMBER, BOXES, FIELD_NAME


def validate_config(config_path):
    """Validates the configuration file against the schema."""
    # Get the absolute path to the schema file
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "scripts", "config.json"))

    with open(config_path, 'r') as config_file, open(schema_path, 'r') as schema_file:
        try:
            config_data = json.load(config_file)
            schema_data = json.load(schema_file)
            jsonschema.validate(instance=config_data, schema=schema_data)
            print('Config file is valid')
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error validating configuration file: {e}")


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
            field_name_value = "Investment Experience"
            field_config = config.get(field_name_value)
            if field_config:
                page_number = field_config[PAGE_NUMBER]
                bbox = field_config.get('investment_experience_radio_bbox', field_config[BOXES])  # Fallback to BOXES if 'investment_experience_radio_bbox' is not present
                if 1 <= page_number <= len(images):
                    text = extract_text_from_bbox(images[page_number - 1], bbox)
                    extracted_data[field_name] = text
                    extracted_data["investment_experience_field_type"] = "radio"  # Indicate radio button type
                else:
                    print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
            else:
                print(f"Field configuration not found for: {field_name} skipping.")

        elif investment_experience_type == "text":
            field_name_value = "Investment Experience"
            field_config = config.get(field_name_value)
            if field_config:
                page_number = field_config[PAGE_NUMBER]
                bbox = field_config.get('investment_experience_text_bbox', field_config[BOXES])  # Fallback to BOXES if 'investment_experience_text_bbox' is not present
                if 1 <= page_number <= len(images):
                    text = extract_text_from_bbox(images[page_number - 1], bbox)
                    extracted_data[field_name] = text
                    extracted_data["investment_experience_field_type"] = "text"  # Indicate text box type
                else:
                    print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
            else:
                print(f"Field configuration not found for: {field_name} skipping.")

        # Process other fields in the order defined in config
        for field_name_value, field_config_list in config.items():
            if field_name_value != "Investment Experience" and field_name_value != "investment_experience_type":
                # Check if it's a list of configs (for multiple methods)
                if isinstance(field_config_list, list):
                    for field_config in field_config_list:
                        page_number = field_config[PAGE_NUMBER]
                        bbox = field_config[BOXES]
                        if 1 <= page_number <= len(images):
                            # Remove gridlines before extraction
                            image_without_gridlines = remove_gridlines_from_image(images[page_number - 1])
                            text = extract_text_from_bbox(image_without_gridlines, bbox)
                            extracted_data[field_name_value] = text
                        else:
                            print(f"Invalid page number ({page_number}) for field: {field_name} skipping.")
                else:  # If not a list, treat as a single config
                    page_number = field_config_list[PAGE_NUMBER]
                    bbox = field_config_list[BOXES]
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
