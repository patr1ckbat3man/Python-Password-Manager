import os
import sys

sys.path.append(os.path.abspath(".."))

from PyQt5.QtWidgets import (
	QApplication, 
	QWidget, 
	QLabel, 
	QLineEdit, 
	QPushButton, 
	QGridLayout, 
	QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import utils.mastermanip as mastermanip
from .storage import StorageWindow
from constants import *

class MasterWindow(QWidget):
	def __init__(self):
		super().__init__()
				
		if not os.path.exists(f"{DB_FOLDER}"):
			os.mkdir(f"{DB_FOLDER}")

		self.hidden_icon = QIcon("icons/hidden.png")
		self.shown_icon = QIcon("icons/shown.png")

		widget = QWidget(self)
		layout = QGridLayout()
		self.label = QLabel()
		self.entry = QLineEdit()
		self.entry.setEchoMode(QLineEdit.Password)
		self.toggle_button = QPushButton()
		self.toggle_button.setIcon(self.hidden_icon)
		self.toggle_button.setIconSize(QSize(19, 19))
		self.toggle_button.setFixedSize(25, 25)
		auth_button = QPushButton("Auth")
		exit_button = QPushButton("Exit")

		self.toggle_button.clicked.connect(self.toggle)
		auth_button.clicked.connect(self.auth)
		exit_button.clicked.connect(QApplication.quit)

		layout.addWidget(self.label, 0, 0)
		layout.addWidget(self.entry, 1, 0, 1, 2)
		layout.addWidget(self.toggle_button, 1, 2)
		layout.addWidget(auth_button, 2, 0)
		layout.addWidget(exit_button, 2, 1)
		layout.setAlignment(Qt.AlignCenter)
		widget.setLayout(layout)

		self.config()
		self.setLayout(layout)
		self.setWindowTitle("Authentication")
		self.setMinimumSize(QSize(650, 400))
		self.show()

	def auth(self):
		key = self.entry.text().encode()
		self.entry.clear()

		if not key:
			QMessageBox.critical(self, "Error!", "Please enter a password.")
			return

		if not os.path.exists(f"{DB_FOLDER}/{DB_MASTER}"):
			mastermanip.write_key(key)
			self.close()
			StorageWindow().show()
		else:
			if mastermanip.verify_key(key):
				self.close()
				StorageWindow().show()
			else:
				QMessageBox.critical(self, "Error!", "Sorry, the password you entered is incorrect or the file you are trying to access is either corrupt or doesn't exist.")

	def toggle(self):
		if self.entry.echoMode() == QLineEdit.Password:
			self.toggle_button.setIcon(self.shown_icon)
			self.entry.setEchoMode(QLineEdit.Normal)
		else:
			self.toggle_button.setIcon(self.hidden_icon)
			self.entry.setEchoMode(QLineEdit.Password)	

	def config(self):
		if os.path.exists(f"{DB_FOLDER}/{DB_MASTER}"):
			self.label.setText(f"Enter master key for {DB_FOLDER}/{DB_STORAGE}")
		else:
			self.label.setText(f"Create master key")