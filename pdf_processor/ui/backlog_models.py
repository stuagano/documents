# Assuming the BacklogRecord class is currently in a file named backlog.py
# and located in the pdf_processor directory.


# 2. Move the class definition
# Find and read the content of the file containing BacklogRecord
with open('pdf_processor/backlog.py', 'r') as f:
    file_content = f.read()

# Extract the BacklogRecord class definition
import re

class_definition = re.search(r'(class BacklogRecord.*?)\n\n', file_content, re.DOTALL)

if class_definition:
    backlog_record_class_code = class_definition.group(1)
    # Update import statements in other files using the BacklogRecord class
    import os
    for root, _, files in os.walk("."):
      for file in files:
        if file.endswith(".py") and file != "backlog.py" and file != "backlog_models.py": #excluding current file and the destination file
          with open(os.path.join(root,file), 'r') as f:
            file_content_other = f.read()
          new_content = file_content_other.replace("from pdf_processor import BacklogRecord", "from pdf_processor.ui.backlog_models import BacklogRecord")
          if new_content != file_content_other:
            with open(os.path.join(root,file), 'w') as f:
              f.write(new_content)
    # Write the class to the new file
    with open('pdf_processor/ui/backlog_models.py', 'w') as f:
        f.write("from typing import List, Dict, Any\n\n") #add necessary imports to the new file
        f.write(backlog_record_class_code)
    