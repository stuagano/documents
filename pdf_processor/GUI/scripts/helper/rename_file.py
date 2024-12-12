#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('sudo pip install ipykernel')


# In[ ]:


get_ipython().system('pip install PyPDF2 pandas')


# In[ ]:


import pandas as pd
from PyPDF2 import PdfReader, PdfWriter


# In[ ]:


df = pd.read_csv('filenames.csv')


# In[ ]:


selected_fields = input("Enter the field names you want to combine (comma-separated): ").split(',')

# Generate filenames
for i in range(len(df)):
  filename = ""
  for field in selected_fields:
    filename += df[field][i] + "_"
  filename = filename.rstrip("_") + ".pdf"  # Remove trailing underscore and add .pdf extension
  print(filename)  # You can replace this with the code to save the PDF page with this filename


# In[ ]:


# Load your PDF
reader = PdfReader("your_pdf_file.pdf")

# Iterate over the pages and save them with the corresponding filenames
for i in range(len(reader.pages)):
  writer = PdfWriter()
  writer.add_page(reader.pages[i])
  with open(df['filename'][i], "wb") as output_file:
    writer.write(output_file)

