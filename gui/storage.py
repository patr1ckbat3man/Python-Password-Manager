import os
import sys

sys.path.append(os.path.abspath(".."))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QSize

import utils.storagemanip as storagemanip
from .data import AddDataWindow
from constants import *

class StorageWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage_handler = storagemanip.DbManip()
        self.data_window = AddDataWindow(self, self.storage_handler)
        self.frames = []

        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.layout = QGridLayout()
        self.add_button = QPushButton("Add entry")
        self.search_button = QPushButton("Search entry")
        self.search_label = QLabel("Search by:")
        self.combo = QComboBox()
        self.combo.addItem("Title")
        self.combo.addItem("URL")
        self.combo.addItem("Username")
        self.search_entry = QLineEdit()
        self.cancel_button = QPushButton("Cancel")
        self.enter_button = QPushButton("Enter")

        self.add_button.clicked.connect(self.data_window.show)
        self.search_button.clicked.connect(self.toggle_widgets)
        self.cancel_button.clicked.connect(self.cancel_search)
        self.enter_button.clicked.connect(self.search)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.add_button, 0, 0)
        self.layout.addWidget(self.search_button, 0, 1)

        self.widget.setLayout(self.layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)
        self.setWindowTitle("Storage")
        self.setMinimumSize(QSize(750, 500))
        self.show()

    def search(self):
        filter_by = self.combo.currentText()
        value = self.search_entry.text()

        if not value:
            QMessageBox.critical(self, "Error!", "Please fill in the search entry.")
            self.search_entry.clear()
        else:
            if not self.storage_handler.table_exists():
                QMessageBox.critical(self, "Error!", "No table to query data from! Add an entry first.")
                self.search_entry.clear()
            else:
                result = self.storage_handler.entry_exists(filter_by, value)
                if not result[0]:
                    QMessageBox.critical(self, "Error!", f"No such entry containing {value} in {filter_by} column.")
                    self.search_entry.clear()
                else:
                    if len(result[1]) == 1:
                        frame = EntryFrame(title=result[1][0][0], username=result[1][0][1], password=result[1][0][2], url=result[1][0][3])
                        self.frames.append(frame)
                        self.layout.addWidget(frame, 3, 1)
                    else:
                        row = 3
                        for i in range(len(result[1])):
                            frame = EntryFrame(title=result[1][i][0], username=result[1][i][1], password=result[1][i][2], url=result[1][i][3])
                            self.frames.append(frame)
                            self.layout.addWidget(frame, row, 1)
                            row += 1

    def cancel_search(self):
        if self.search_label.isVisible() and self.combo.isVisible():
            self.search_label.setVisible(False)
            self.combo.setVisible(False)
            self.search_entry.setVisible(False)
            self.enter_button.setVisible(False)
            self.cancel_button.setVisible(False)
            self.add_button.setVisible(True)
            self.search_button.setVisible(True)
            for frame in self.frames:
                frame.setVisible(False)

    def toggle_widgets(self):
        if self.search_entry.isVisible() and \
        self.combo.isVisible():
            self.search_label.setVisible(False)
            self.combo.setVisible(False)
            self.search_entry.setVisible(False)
        else:
            self.search_label.setVisible(True)
            self.combo.setVisible(True)
            self.search_entry.setVisible(True)
            self.enter_button.setVisible(True)
            self.cancel_button.setVisible(True)
            self.add_button.setVisible(False)
            self.search_button.setVisible(False)

            self.layout.addWidget(self.search_label, 0, 0)
            self.layout.addWidget(self.combo, 0, 1)
            self.layout.addWidget(self.search_entry, 1, 0, 1, 2)
            self.layout.addWidget(self.cancel_button, 2, 0)
            self.layout.addWidget(self.enter_button, 2, 1)


    def closeEvent(self, event):
    	reply = QMessageBox.question(self, "Quit?", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    	if reply == QMessageBox.Yes:
    		self.storage_handler.close()
    		event.accept()
    	else:
    		event.ignore()

class EntryFrame(QFrame):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

        self.delete_button = QPushButton("Delete", self)
        self.edit_button = QPushButton("Edit", self)

        self.setStyleSheet("QFrame {border: 1px solid #7f7f7f; padding: 3px;}")

        for k, v in self.kwargs.items():
            setattr(self, k, v)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.create_widgets()

    def create_widgets(self):
        row = 0
        for k, v in self.kwargs.items():
            label = QLabel(k)
            value = QLabel(v)
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(value, row, 1)
            row += 1
        self.layout.addWidget(self.delete_button, row+1, 0)
        self.layout.addWidget(self.edit_button, row+1, 1)