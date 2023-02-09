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

        self.initUI()
        """

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.add_button = QPushButton("Add entry", central_widget)

        self.search_button = QPushButton("Search entry", central_widget)
        self.search_entry = QLineEdit(central_widget)
        self.search_entry.setVisible(False)

        self.search_by = QLabel("Search by", central_widget)
        self.search_by.setVisible(False)

        self.enter_button = QPushButton("Enter", central_widget)
        self.enter_button.setVisible(False)

        self.cancel_button = QPushButton("Cancel", central_widget)
        self.cancel_button.setVisible(False)

        self.combo = QComboBox(central_widget)
        self.combo.addItem("Title")
        self.combo.addItem("URL")
        self.combo.addItem("Username")
        self.combo.setVisible(False)

        self.storage_grid = QGridLayout(central_widget)
        self.storage_grid.addWidget(self.add_button, 0, 0)
        self.storage_grid.addWidget(self.search_button, 0, 1)

       	self.add_button.clicked.connect(self.data_window.show)
        self.search_button.clicked.connect(self.toggle_widgets)
        self.enter_button.clicked.connect(self.search)
        self.cancel_button.clicked.connect(self.cancel_search)

        self.storage_grid.setAlignment(Qt.AlignCenter)
        """

    def initUI(self):
    	self.scroll = QScrollArea()
    	self.widget = QWidget()
    	self.vbox = QVBoxLayout()

    	for i in range(1, 50):
    		object = QLabel("AHOJ")
    		self.vbox.addWidget(object)

    	self.widget.setLayout(self.vbox)
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
	    			self.storage_grid.addWidget(frame, 4, 1)
	    		else:
	    			row = 4
	    			for i in range(len(result[1])):
	    				#print(result[1][i])
	    				frame = EntryFrame(title=result[1][i][0], username=result[1][i][1], password=result[1][i][2], url=result[1][i][3])
	    				self.storage_grid.addWidget(frame, row, 1)
	    				row += 1

    def cancel_search(self):
    	if self.search_by.isVisible() and \
        self.combo.isVisible() and \
        self.search_entry.isVisible() and \
        self.enter_button.isVisible() and \
        self.cancel_button.isVisible():
    		self.search_by.setVisible(False)
    		self.combo.setVisible(False)
    		self.search_entry.setVisible(False)
    		self.enter_button.setVisible(False)
    		self.cancel_button.setVisible(False)
    		self.add_button.setVisible(True)
    		self.search_button.setVisible(True)

    def toggle_widgets(self):
    	if self.search_entry.isVisible() and \
        self.combo.isVisible():
    		self.search_by.setVisible(False)
    		self.combo.setVisible(False)
    		self.search_entry.setVisible(False)
    	else:
    		self.search_by.setVisible(True)
    		self.combo.setVisible(True)
    		self.search_entry.setVisible(True)
    		self.enter_button.setVisible(True)
    		self.cancel_button.setVisible(True)
    		self.add_button.setVisible(False)
    		self.search_button.setVisible(False)

    		self.storage_grid.addWidget(self.search_by, 1, 0, 1, 1)
    		self.storage_grid.addWidget(self.combo, 1, 1, 1, 1)
    		self.storage_grid.addWidget(self.search_entry, 2, 0, 1, 2)
    		self.storage_grid.addWidget(self.enter_button, 3, 0, 1, 1)
    		self.storage_grid.addWidget(self.cancel_button, 3, 1, 1, 1)

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