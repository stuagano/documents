import json
import sqlite3
import os

def create_database(config_dir="pdf_processor/ui/scripts/configs", db_file="all_data.db"):
    all_fields = set()
    for filename in os.listdir(config_dir):
        if filename.endswith(".json") and filename != "all_data_config.json":
            filepath = os.path.join(config_dir, filename)
            try:
                with open(filepath, "r") as f:
                    config_data = json.load(f)
                    if "fields_to_extract" in config_data:
                        all_fields.update(config_data["fields_to_extract"])
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error processing {filename}: {e}")
                continue

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        columns = ", ".join([f"{field} TEXT" for field in all_fields])
        create_table_query = f"CREATE TABLE IF NOT EXISTS extracted_data (page_number INTEGER, {columns})"
        cursor.execute(create_table_query)

        conn.commit()
        conn.close()
        print(f"Database '{db_file}' created with table 'extracted_data'")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")


if __name__ == "__main__":
    create_database()