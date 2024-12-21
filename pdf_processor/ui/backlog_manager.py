
import logging
import os
from PyQt5.QtWidgets import QInputDialog, QMessageBox

logger = logging.getLogger(__name__)

class BacklogRecord:
    def __init__(self, document_name, page_number, field_name, pdf_path):
        self.document_name = document_name
        self.page_number = page_number
        self.field_name = field_name
        self.pdf_path = pdf_path

class BacklogManager:
    def __init__(self, database_manager, ui_instance):
        self.backlog_queue = []
        self.database_manager = database_manager
        self.ui_instance = ui_instance

    def add_to_backlog(self, pdf_path, page_number, field_name):
        self.backlog_queue.append(BacklogRecord(os.path.basename(pdf_path), page_number, field_name, pdf_path))

    def update_backlog_list(self, backlog_list_widget):
        backlog_list_widget.clear()
        for record in self.backlog_queue:
            item_text = f"{record.document_name} - Page {record.page_number} - {record.field_name}"
            backlog_list_widget.addItem(item_text)

    def update_record_value(self, document_name, page_number, field_name, new_value):
        try:
            self.database_manager.update_record("records_to_be_validated", {"field_value": new_value},
                                                 f"document_name = '{document_name}' AND page_number = {page_number} AND field_name = '{field_name}'")

            logger.info(f"Updated record: {document_name}, Page: {page_number}, Field: {field_name}, New Value: {new_value}")
        except Exception as e:
            logger.exception(f"Error updating record value: {e}")
            QMessageBox.critical(self.ui_instance, "Error", f"Error updating record value: {e}")

    def review_backlog(self, backlog_list_widget):
        if not self.backlog_queue:
            QMessageBox.information(self.ui_instance, "Information", "Backlog queue is empty.")
            return

        try:
            for record in self.backlog_queue[:]:
                new_value, ok = QInputDialog.getText(
                    self.ui_instance, "Backlog Review", f"Enter new value for {record.field_name} (or press Enter to skip): "
                )
                if ok and new_value:
                    self.update_record_value(record.document_name, record.page_number, record.field_name, new_value)
                    self.backlog_queue.remove(record)
                    self.update_backlog_list(backlog_list_widget)
                    QMessageBox.information(self.ui_instance, "Information", "Record updated successfully.")
                else:
                    QMessageBox.information(self.ui_instance, "Information", "Skipping record...")
        except Exception as e:
            QMessageBox.critical(self.ui_instance, "Error", f"An error occurred while reviewing the backlog: {e}")
            logging.exception(f"Error reviewing backlog: {e}")

import os
