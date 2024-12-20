import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import messagebox
import json
from pdf_processor.core import process_documents

CONFIG_DIR = "pdf_processor/ui/scripts/configs"


# Create the ui_utils.py file if it doesn't exist.
ui_utils_path = "pdf_processor/ui/ui_utils.py"
if not os.path.exists(ui_utils_path):
    with open(ui_utils_path, "w") as f:
        f.write("")  # Create an empty file


# Read the contents of simple_ui.py
simple_ui_path = "pdf_processor/ui/simple_ui.py"
try:
    with open(simple_ui_path, "r") as f:
        simple_ui_content = f.read()
except FileNotFoundError:
    print(f"Error: File '{simple_ui_path}' not found.")
    simple_ui_content = ""

# Regular expression to identify functions (simplified, might need adjustment)
import re
function_pattern = r"def\s+(\w+)\s*\(.*?\):"

# Find all functions in simple_ui.py
functions = re.findall(function_pattern, simple_ui_content)


# Move function definitions to ui_utils.py
with open(ui_utils_path, "a") as ui_utils_file:
  for function in functions:
    # Find function definition and its body.
    function_definition = re.search(rf"def\s+{function}\s*\(.*?\):(.*?)(?=\n\s*def|$)", simple_ui_content, re.DOTALL)
    if function_definition:
      ui_utils_file.write(function_definition.group(0) + "\n")
    
    #Replace function in simple_ui with import.
    simple_ui_content = re.sub(rf"def\s+{function}\s*\(.*?\):(.*?)(?=\n\s*def|$)", "", simple_ui_content, flags = re.DOTALL)


#Update simple_ui.py to import moved functions
with open(simple_ui_path, "w") as f:
    f.write("from .ui_utils import *\n\n") #Import all functions from ui_utils
    f.write(simple_ui_content)


def load_config_options(configs_dir):
    """Gets the config files from the configs directory and returns a list of strings."""
    config_options = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    if not config_options:
        messagebox.showerror("Error", f"No config files found in the '{CONFIG_DIR}' directory.")
        return [] 
    return config_options


def load_config_options(configs_dir):
    """Gets the config files from the configs directory and returns a list of strings."""
    config_options = [f for f in os.listdir(configs_dir) if f.endswith(".json")]
    if not config_options:
        messagebox.showerror("Error", "No config files found in the 'configs' directory.")
        return []  # Return an empty list if no config files are found
    return config_options


def create_config_picklists(self):
    """Creates the config file picklists."""
    config_options = load_config_options(
        os.path.join(os.path.dirname(__file__), "scripts", "configs")
    )
    if not config_options:  # If no config files were found, exit the function
        return

    self.config_var.set(config_options[0])  # Set the first option as default

    self.config_dropdown = tk.OptionMenu(self.root, self.config_var, *config_options)
    self.config_dropdown.grid(row=0, column=1, padx=5, pady=5)

    self.output_dir_var.set(self.default_output_dir)  # Setting default output directory


def create_config_picklists_ui(self):
    """Creates the config file picklists."""
    self.config_var = tk.StringVar(self.root)
    self.config_var.set("Select Config")  # Default value

    config_options = [f for f in os.listdir(self.configs_dir) if f.endswith(".json")]
    self.config_dropdown = tk.OptionMenu(self.root, self.config_var, *config_options)
    self.config_dropdown.grid(row=0, column=1, padx=5, pady=5)

    self.output_dir_var = tk.StringVar(self.root)
    self.output_dir_var.set(self.default_output_dir)

    output_dir_label = tk.Label(self.root, text="Output Directory:")
    output_dir_label.grid(row=1, column=0, padx=5, pady=5)

    output_dir_entry = tk.Entry(self.root, textvariable=self.output_dir_var, width=40)
    output_dir_entry.grid(row=1, column=1, padx=5, pady=5)


def _compare_images(image1_path, image2_path):
    """Compares two images and returns True if they are similar, False otherwise."""
    try:
        # Open images using Pillow
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Ensure images are in the same mode (e.g., RGB)
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")

        # Compare images
        return img1.tobytes() == img2.tobytes()

    except FileNotFoundError:
        print(f"Error: One or both image files not found: {image1_path}, {image2_path}")
        return False
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False


def _show_image_comparison_dialog(self, image1_path, image2_path):
    """Shows a dialog with the two images for comparison."""
    comparison_window = tk.Toplevel(self.root)
    comparison_window.title("Image Comparison")

    # Load and resize images
    try:
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Resize images to fit the window
        max_width = 600
        max_height = 400
        img1.thumbnail((max_width, max_height))
        img2.thumbnail((max_width, max_height))

        # Convert images to Tkinter PhotoImage objects
        photo1 = ImageTk.PhotoImage(img1)
        photo2 = ImageTk.PhotoImage(img2)

        # Create labels to display images
        label1 = tk.Label(comparison_window, image=photo1)
        label1.image = photo1  # Keep a reference to avoid garbage collection
        label1.grid(row=0, column=0, padx=10, pady=10)

        label2 = tk.Label(comparison_window, image=photo2)
        label2.image = photo2
        label2.grid(row=0, column=1, padx=10, pady=10)

    except FileNotFoundError:
        messagebox.showerror("Error", "One or both image files not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    # Center the comparison window
    comparison_window.update_idletasks()  # Update window size
    width = comparison_window.winfo_width()
    height = comparison_window.winfo_height()
    x = (comparison_window.winfo_screenwidth() // 2) - (width // 2)
    y = (comparison_window.winfo_screenheight() // 2) - (height // 2)
    comparison_window.geometry(f"+{x}+{y}")


def load_pdf(pdf_path):
    """Loads a PDF file and returns a PyMuPDF Document object."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        return doc
    except ImportError:
        messagebox.showerror(
            "Error",
            "PyMuPDF is not installed. Please install it using 'pip install pymupdf'."
        )
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the PDF: {e}")
        return None


def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def extract_data_from_pdf_with_config(pdf_path, config_path):
    """Extracts data from a PDF file using the specified config file."""
    try:
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

        extracted_data = process_documents.extract_data_from_pdf(pdf_path, config_data)

        return extracted_data

    except FileNotFoundError:
        messagebox.showerror("Error", f"Config file not found: {config_path}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"Invalid JSON in config file: {config_path}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during data extraction: {e}")
        return None

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def load_and_display_pdf(self, pdf_path):
    """Loads and displays the PDF in the canvas."""
    doc = load_pdf(pdf_path)
    if doc is None:
        return  # Exit if PDF loading failed

    self.doc = doc  # Store the document object
    self.current_page = 0

    self.display_page(self.current_page)

    # Update page label
    self.page_label.config(text=f"Page {self.current_page + 1} of {len(self.doc)}")

    # Enable/disable navigation buttons
    self.prev_button.config(state="disabled" if self.current_page == 0 else "normal")
    self.next_button.config(
        state="disabled" if self.current_page == len(self.doc) - 1 else "normal"
    )


def display_page(self, page_num):
    """Displays the specified page of the PDF in the canvas."""
    page = self.doc[page_num]
    zoom = 1.5  # Adjust zoom as needed
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # Convert pixmap to Tkinter-compatible image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    self.photo = ImageTk.PhotoImage(image=img)  # Keep a reference!

    # Clear canvas and display image
    self.canvas.delete("all")
    self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    # Update canvas scroll region
    self.canvas.config(scrollregion=self.canvas.bbox("all"))


def _on_mousewheel(self, event):
    """Handles mousewheel scrolling for the canvas."""
    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def process_pdf(self):
    """Processes the selected PDF file with the chosen config."""
    pdf_path = self.pdf_path_var.get()
    config_name = self.config_var.get()
    output_dir = self.output_dir_var.get()

    if not pdf_path or not config_name or not output_dir:
        messagebox.showerror("Error", "Please select a PDF file, config file, and output directory.")
        return

    config_path = os.path.join(self.configs_dir, config_name)

    try:
        extracted_data = extract_data_from_pdf_with_config(pdf_path, config_path)

        if extracted_data:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Generate output file path
            pdf_filename = os.path.basename(pdf_path)
            output_filename = os.path.splitext(pdf_filename)[0] + "_extracted_data.json"
            output_path = os.path.join(output_dir, output_filename)

            # Save extracted data to JSON file
            with open(output_path, "w") as output_file:
                json.dump(extracted_data, output_file, indent=4)

            messagebox.showinfo("Success", f"Data extracted and saved to: {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing: {e}")

def process_pdf(self):
    """Processes the selected PDF file with the chosen config."""
    pdf_path = self.pdf_path_var.get()
    config_name = self.config_var.get()
    output_dir = self.output_dir_var.get()
    # Additional logic for processing the PDF with the selected configuration
    # ...

