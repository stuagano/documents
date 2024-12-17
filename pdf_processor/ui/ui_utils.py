import os

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

print(f"Functions moved to {ui_utils_path}")