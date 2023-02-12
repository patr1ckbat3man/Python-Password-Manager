import os
import sys

sys.path.append(os.path.abspath(".."))

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow, 
    QWidget, 
    QGridLayout, 
    QLabel, 
    QComboBox, 
    QLineEdit, 
    QPushButton, 
    QMessageBox, 
    QScrollArea, 
    QFrame
)
from PyQt5.QtCore import Qt, QSize

import utils.storagemanip as storagemanip
from .data import AddDataWindow
from .frame import Frame
from constants import *

class StorageWindow(QMainWindow):
    def __init__(self, master_key):
        super().__init__()
        self.master_key = master_key
        self.storage_handler = storagemanip.DbManip(self.master_key)
        self.data_window = AddDataWindow(self, self.storage_handler)

        self.widget = QWidget(self)
        self.layout = QGridLayout()
        self.add_button = QPushButton("Add entry")
        self.search_button = QPushButton("Search entry")

        self.label = QLabel("Search by")
        self.combo = QComboBox()
        self.combo.addItem("Title")
        self.combo.addItem("Username")
        self.combo.addItem("URL")
        self.search_entry = QLineEdit()
        self.cancel_button = QPushButton("Cancel")
        self.enter_button = QPushButton("Enter")

        self.add_button.clicked.connect(self.data_window.show)
        self.search_button.clicked.connect(self.toggle)
        self.cancel_button.clicked.connect(self.cancel)
        self.enter_button.clicked.connect(self.search)

        self.layout.addWidget(self.add_button, 0, 0)
        self.layout.addWidget(self.search_button, 0, 1)
        self.layout.setAlignment(Qt.AlignCenter)
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("Storage")
        self.setMinimumSize(QSize(750, 500))
        self.show()

    def search(self):
        filter_by = self.combo.currentText()
        value = self.search_entry.text()
        self.frames = []
        self.storage_handler.decrypt()

        if not value:
            QMessageBox.critical(self, "Error!", "Please fill in the search entry.")
            return

        if not self.storage_handler.table_exists():
            QMessageBox.critical(self, "Error!", "No entries to search from. Add an entry first!")
            return

        result = self.storage_handler.entry_exists(filter_by, value)

        if not result[0]:
            QMessageBox.critical(self, "Error!", f"No such entry containing {value} in {filter_by} column.")
            return

        row = 3
        for i in range(len(result[1])):
            title = result[1][i][0]
            username = result[1][i][1]
            password = result[1][i][2]
            url = result[1][i][3]
            frame = Frame(
                title=title,
                username=username,
                password=password,
                url=url,
            )
            self.frames.append(frame)
            self.layout.addWidget(frame, row, 1)
            row += 1

    def cancel(self):
        if self.label.isVisible() and self.combo.isVisible():
            self.label.setVisible(False)
            self.combo.setVisible(False)
            self.search_entry.setVisible(False)
            self.enter_button.setVisible(False)
            self.cancel_button.setVisible(False)
            self.add_button.setVisible(True)
            self.search_button.setVisible(True)
            for frame in self.frames:
                frame.setVisible(False)

    def toggle(self):
        if self.search_entry.isVisible() and self.combo.isVisible():
            self.label.setVisible(False)
            self.combo.setVisible(False)
            self.search_entry.setVisible(False)
        else:
            self.add_button.setVisible(False)
            self.search_button.setVisible(False)
            self.label.setVisible(True)
            self.combo.setVisible(True)
            self.search_entry.setVisible(True)
            self.enter_button.setVisible(True)
            self.cancel_button.setVisible(True)

            self.layout.addWidget(self.label, 0, 0)
            self.layout.addWidget(self.combo, 0, 1)
            self.layout.addWidget(self.search_entry, 1, 0, 1, 2)
            self.layout.addWidget(self.cancel_button, 2, 0)
            self.layout.addWidget(self.enter_button, 2, 1)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Quit?", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.storage_handler.encrypt()

        if reply == QMessageBox.Yes:
            self.storage_handler.close()
            event.accept()
        else:
            event.ignore()