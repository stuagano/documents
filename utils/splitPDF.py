import os
import sys
import re
import pandas as pd

def rename_pdfs(input_directory, output_directory, mapping_file):
    if not os.path.isdir(input_directory):
        print(f"Invalid input directory: {input_directory}")
        sys.exit(1)
    
    os.makedirs(output_directory, exist_ok=True)
    
    # Load renaming mapping from a CSV file
    mapping_path = os.path.join(input_directory, mapping_file)
    if not os.path.exists(mapping_path):
        print(f"Mapping file not found: {mapping_path}")
        sys.exit(1)
    
    df = pd.read_csv(mapping_path)
    
    for index, row in df.iterrows():
        original_name = row['original_filename']
        new_name = row['new_filename']
        
        original_path = os.path.join(input_directory, original_name)
        new_path = os.path.join(output_directory, new_name)
        
        if os.path.exists(original_path):
            try:
                os.rename(original_path, new_path)
                print(f"Renamed '{original_name}' to '{new_name}'")
            except Exception as e:
                print(f"Error renaming '{original_name}': {e}")
        else:
            print(f"File not found: {original_path}")

def main(input_directory, output_directory, mapping_file='rename_mapping.csv'):
    rename_pdfs(input_directory, output_directory, mapping_file)

if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python splitPDF.py <input_directory> <output_directory> [<mapping_file>]")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    mapping_file = sys.argv[3] if len(sys.argv) == 4 else 'rename_mapping.csv'
    
    main(input_dir, output_dir, mapping_file)