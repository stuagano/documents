import sqlite3
import json
import time
from typing import Dict, List, Tuple, Union, Any
import os


class DatabaseManager:
    def __init__(self, db_name: str = "extracted_data.db"):
        self.db_name = db_name
        self.connection = self.connect_to_database()
        self.DATABASE_SCHEMA = {
            'completed_records': {
                'document_name': 'TEXT',
                'page_number': 'INTEGER',
                'field_name': 'TEXT',
                'field_value': 'TEXT',
                'account_number': 'TEXT',
                'box_x': 'INTEGER',
                'box_y': 'INTEGER',
                'box_width': 'INTEGER',
                'box_height': 'INTEGER',
                'status': 'TEXT'
            },
            'records_to_be_validated': {
                'document_name': 'TEXT',
                'page_number': 'INTEGER',
                'field_name': 'TEXT',
                'field_value': 'TEXT',
                'account_number': 'TEXT',
                'box_x': 'INTEGER',
                'box_y': 'INTEGER',
                'box_width': 'INTEGER',
                'box_height': 'INTEGER'
            }
        }
        self.create_tables()

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

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.connection.cursor()

    def get_database_schema(self):
        return self.DATABASE_SCHEMA

    def create_tables(self):
        """Creates the necessary database tables if they don't exist."""
        try:
            with self.connection:
                cursor = self.connection.cursor()
                for table_name, columns in self.DATABASE_SCHEMA.items():
                    column_definitions = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
                    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
                    cursor.execute(create_table_query)
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

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

    def save_extracted_text(self, image_id: int, section: str, text: str) -> None:
        """Save extracted text for an image section."""
        query = """
            INSERT INTO extracted_text (image_id, section, text)
            VALUES (?, ?, ?)
        """
        self._execute_query(query, (image_id, section, text))

    def get_image_data(self, image_id: int) -> dict:
        """Retrieve all data for an image."""
        query = "SELECT * FROM images WHERE id = ?"
        return self._execute_query(query, (image_id,), fetch_one=True)

    def save_bounding_boxes(self, image_id: int, boxes: dict) -> None:
        """Save bounding box coordinates."""
        query = """
            INSERT INTO bounding_boxes (image_id, section, x, y, width, height)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        for section, (x, y, width, height) in boxes.items():
            self._execute_query(query, (image_id, section, x, y, width, height))

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """Execute SQL query with error handling."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise