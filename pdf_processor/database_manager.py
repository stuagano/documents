import sqlite3
import json
import time
from typing import Dict, List, Tuple, Union, Any
import os


class DatabaseManager:
    def __init__(self, db_name: str = "extracted_data.db", schema_file_path: str = "schema.json"):
        self.db_name = db_name
        self.schema_file_path = schema_file_path
        self.connection = self.connect_to_database()

    def connect_to_database(self, max_retries=3, retry_delay=1):
        for attempt in range(max_retries):
            try:
                connection = sqlite3.connect(self.db_name)
                return connection
            except sqlite3.Error as e:
                print(f"Error connecting to database: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise

    def get_database_schema(self) -> Dict:
        try:
            with open(self.schema_file_path, "r") as schema_file:
                schema = json.load(schema_file)
                return schema
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found at {self.schema_file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in schema file at {self.schema_file_path}")

    def create_tables(self, schema: Dict):
        """
        Creates tables in the database based on the provided schema.

        Args:
            schema (Dict): A dictionary representing the database schema.
                           Keys are table names, values are dictionaries containing column names and types.
        """
        with self.connection:
            cursor = self.connection.cursor()
            for table_name, table_schema in schema.items():
                columns = ", ".join([f"{column_name} {column_type}" for column_name, column_type in table_schema.items()])
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
                cursor.execute(create_table_query)

    def create_tables_from_config(self, config_path: str):
        """
        Creates database tables based on the schema defined in config files.

        Args:
            config_path: The path to the directory containing config files.
        """
        schema = {}
        for filename in os.listdir(config_path):
            if filename.endswith(".json"):
                filepath = os.path.join(config_path, filename)
                with open(filepath, 'r') as f:
                    config_data = json.load(f)
                    table_name = config_data.get("table_name", filename[:-5])  # Default to filename without .json
                    fields = config_data.get("global_fields", {})
                    fields.update(config_data.get("fields", {}))  # Merge global and page-specific fields
                    schema[table_name] = fields
        self.create_tables(schema)

    def insert_record(self, table_name: str, record_data: Dict):
        """
        Inserts a record into the specified table.

        Args:
            table_name (str): The name of the table to insert into.
            record_data (Dict): A dictionary containing the data to insert.
                                Keys are column names, values are the corresponding data.
        """
        schema = self.get_database_schema().get(table_name)
        if schema:
            record_data = self.validate_and_convert_data_types(record_data, schema)
        with self.connection:
            cursor = self.connection.cursor()
            columns = ", ".join(record_data.keys())
            placeholders = ", ".join(["?"] * len(record_data))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(record_data.values()))

    def fetch_records(self, table_name: str) -> List[Tuple]:
        """Fetches all records from the specified table."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

    def fetch_record(self, table_name: str, condition: str) -> Union[Tuple, None]:
        """Fetches a single record from the specified table based on a condition."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE {condition}")
            return cursor.fetchone()

    def record_exists(self, table_name: str, condition: str) -> bool:
        """Checks if a record exists in the specified table based on a condition."""
        return self.fetch_record(table_name, condition) is not None

    def fetch_all_records_with_condition(self, table_name: str, condition: str) -> List[Tuple]:
        """Fetches all records from the specified table that match a certain condition."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE {condition}")
            return cursor.fetchall()

    def update_record(self, table_name: str, record_data: Dict, condition: str):
        """Updates a record in the specified table based on a condition."""
        schema = self.get_database_schema().get(table_name)
        if schema:
            record_data = self.validate_and_convert_data_types(record_data, schema)
        with self.connection:
            cursor = self.connection.cursor()
            updates = ", ".join([f"{column} = ?" for column in record_data.keys()])
            update_query = f"UPDATE {table_name} SET {updates} WHERE {condition}"
            cursor.execute(update_query, tuple(record_data.values()))

    def delete_record(self, table_name: str, condition: str):
        cursor = self.connection.cursor()
        delete_query = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(delete_query)
        self.connection.commit()

    def handle_duplicate_account_number(self, ui_instance, existing_record, new_record):
        """Handles duplicate account numbers by displaying a dialog to the user."""
        ui_instance.handle_duplicate_account_number(existing_record, new_record)

    def move_record(self, from_table: str, to_table: str, condition: str):
        """Moves a record from one table to another."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO {to_table} SELECT * FROM {from_table} WHERE {condition}")
            cursor.execute(f"DELETE FROM {from_table} WHERE {condition}")

    def validate_and_convert_data_types(self, data_dict: dict, schema: dict) -> dict:
        """Validates and converts data types based on the schema."""
        validated_data = {}
        for column_name, value in data_dict.items():
            if column_name in schema:
                column_type = schema[column_name]
                try:
                    if column_type == "INTEGER":
                        validated_data[column_name] = int(value)
                    elif column_type == "REAL":
                        validated_data[column_name] = float(value)
                    elif column_type == "TEXT":
                        validated_data[column_name] = str(value)
                    else:
                        validated_data[column_name] = value  # Unknown type, keep as is
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert value '{value}' for column '{column_name}' to type '{column_type}'. Keeping original value.")
                    validated_data[column_name] = value
            else:
                validated_data[column_name] = value  # Column not in schema, keep as is
        return validated_data

    def fetch_columns(self, table_name: str) -> List[str]:
        """Fetches the column names of a table."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            return columns

    def close_connection(self):
        if self.connection:
            self.connection.close()