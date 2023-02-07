import secrets
import os
from string import ascii_letters, digits, punctuation

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from db import DbManip
from master import MasterManip
from constants import *

class MasterPromptWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Authentication")
		self.setMinimumSize(QSize(650, 400))

		self.master_handler = MasterManip()

		self.hidden_icon = QIcon("icons/hidden.png")
		self.shown_icon = QIcon("icons/shown.png")

		self.label = QLabel(self)
		self.entry = QLineEdit(self)
		self.entry.setEchoMode(QLineEdit.Password)

		self.visibility_button = QPushButton(self)
		self.visibility_button.setIcon(self.hidden_icon)
		self.visibility_button.setIconSize(QSize(19, 19))
		self.visibility_button.setFixedSize(25, 25)
		self.visibility_button.clicked.connect(self.toggle_visibility)

		auth_button = QPushButton("Auth", self)
		auth_button.clicked.connect(self.auth_user)

		exit_button = QPushButton("Exit", self)
		exit_button.clicked.connect(QApplication.quit)

		master_grid = QGridLayout()
		master_grid.addWidget(self.label, 0, 0)
		master_grid.addWidget(self.entry, 1, 0, 1, 2)
		master_grid.addWidget(self.visibility_button, 1, 2)
		master_grid.addWidget(auth_button, 2, 0)
		master_grid.addWidget(exit_button, 2, 1)
		master_grid.setAlignment(Qt.AlignCenter)

		self.setLayout(master_grid)
		self.config_label()

	def auth_user(self):
		storage_window = StorageWindow()
		key = self.entry.text().encode()
		self.entry.clear()

		if not os.path.exists(f"{DB_FOLDER}/{DB_MASTER}"):
			self.master_handler.write_key(key)
			self.close()
			storage_window.show()
		else:
			if self.master_handler.verify_key(key):
				self.close()
				storage_window.show()
			else:
				QMessageBox.critical(self, "Error!", "Sorry, the password you entered is incorrect or the file you are trying to access is either corrupt or doesn't exist.")

	def toggle_visibility(self):
		if self.entry.echoMode() == QLineEdit.Password:
			self.visibility_button.setIcon(self.shown_icon)
			self.entry.setEchoMode(QLineEdit.Normal)
		else:
			self.visibility_button.setIcon(self.hidden_icon)
			self.entry.setEchoMode(QLineEdit.Password)	

	def config_label(self):
		if os.path.exists(f"{DB_FOLDER}/{DB_MASTER}"):
			self.label.setText(f"Enter master key for {DB_FOLDER}/{DB_STORAGE}")
		else:
			self.label.setText(f"Create master key")

class StorageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Storage")
        self.setMinimumSize(QSize(750, 500))

        self.storage_handler = DbManip()
        self.data_window = AddDataWindow(self, self.storage_handler)

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

    def search(self):
    	filter_by = self.combo.currentText()
    	value = self.search_entry.text()
    	if not self.storage_handler.table_exists():
    		QMessageBox.critical(self, "Error!", "No table to search data from!")
    		self.search_entry.clear()
    	else:
	    	if not self.storage_handler.entry_exists(filter_by, value):
	    		QMessageBox.critical(self, "Error!", f"No such entry containing {value} in {filter_by} column.")
	    		self.search_entry.clear()
	    	else:
	    		print("containing.")

    def closeEvent(self, event):
    	reply = QMessageBox.question(self, "Quit?", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    	if reply == QMessageBox.Yes:
    		self.storage_handler.close()
    		event.accept()
    	else:
    		event.ignore()

    def cancel_search(self):
    	if self.search_by.isVisible() and self.combo.isVisible() \
    		and self.search_entry.isVisible() and self.enter_button.isVisible() \
    		and self.cancel_button.isVisible():
    		self.search_by.setVisible(False)
    		self.combo.setVisible(False)
    		self.search_entry.setVisible(False)
    		self.enter_button.setVisible(False)
    		self.cancel_button.setVisible(False)
    		self.add_button.setVisible(True)
    		self.search_button.setVisible(True)


    def toggle_widgets(self):
    	if self.search_entry.isVisible() and self.combo.isVisible():
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

class AddDataWindow(QWidget):
	def __init__(self, parent, obj):
		super().__init__()
		self.setWindowTitle("Add entry")
		self.setMinimumSize(QSize(650, 450))

		self.parent = parent
		self.storage_handler = obj

		self.hidden_icon = QIcon("icons/hidden.png")
		self.shown_icon = QIcon("icons/shown.png")

		self.title_label = QLabel("Title:", self)
		self.title_entry = QLineEdit(self)

		self.username_label = QLabel("Username:", self)
		self.username_entry = QLineEdit(self)

		self.password_label = QLabel("Password:", self)
		self.password_entry = QLineEdit(self)
		self.password_entry.setEchoMode(QLineEdit.Password)

		self.repeat_password_label = QLabel("Repeat password:", self)
		self.repeat_password_entry = QLineEdit(self)
		self.repeat_password_entry.setEchoMode(QLineEdit.Password)

		self.generate_password_button = QPushButton("Generate", self)
		self.visibility_button = QPushButton(self)
		self.visibility_button.setIcon(self.hidden_icon)
		self.visibility_button.setIconSize(QSize(19, 19))
		self.visibility_button.setFixedSize(25, 25)
		self.spin_box = QSpinBox(self)
		self.spin_box.setRange(1, 64)
		self.spin_box.setValue(16)

		self.url_label = QLabel("URL:", self)
		self.url_entry = QLineEdit(self)

		self.submit_button = QPushButton("Add", self)

		self.generate_password_button.clicked.connect(self.populate_password)
		self.visibility_button.clicked.connect(self.toggle_visibility)
		self.submit_button.clicked.connect(self.add_entry)

		grid = QGridLayout()
		grid.addWidget(self.title_label, 0, 0)
		grid.addWidget(self.title_entry, 0, 1)
		grid.addWidget(self.username_label, 1, 0)
		grid.addWidget(self.username_entry, 1, 1)
		grid.addWidget(self.password_label, 2, 0)
		grid.addWidget(self.password_entry, 2, 1)
		grid.addWidget(self.generate_password_button, 2, 2)
		grid.addWidget(self.spin_box, 2, 3)
		grid.addWidget(self.repeat_password_label, 3, 0)
		grid.addWidget(self.repeat_password_entry, 3, 1)
		grid.addWidget(self.visibility_button, 3, 2)
		grid.addWidget(self.url_label, 4, 0)
		grid.addWidget(self.url_entry, 4, 1)
		grid.addWidget(self.submit_button, 5, 1)

		self.setLayout(grid)
		grid.setAlignment(Qt.AlignCenter)

	def validate_entry(self):
		title = self.title_entry.text()
		password = self.password_entry.text()
		repeat_password = self.repeat_password_entry.text()

		if not title:
			QMessageBox.critical(self, "Error!", "Please make sure the title entry is filled in.")
			return False
		if password != repeat_password:
			QMessageBox.critical(self, "Error!", "The passwords do not match. Please re-enter your passwords.")
			return False
		if not password or not repeat_password:
			QMessageBox.critical(self, "Error!", "Please make sure both the password entries are filled in.")
			return False
		return True

	def add_entry(self):
		if self.validate_entry():
			self.storage_handler.create_storage()

			title = self.title_entry.text()
			username = self.username_entry.text()
			password = self.password_entry.text()
			url = self.url_entry.text()

			self.title_entry.clear()
			self.username_entry.clear()
			self.password_entry.clear()
			self.repeat_password_entry.clear()
			self.url_entry.clear()

			self.storage_handler.add(title=title, username=username, password=password, url=url)
			self.close()
			QMessageBox.information(self.parent, "Success!", "Entry succesfully added.")

	def populate_password(self):
		length = self.spin_box.value()
		generated_password = self.generate_password(length)
		self.password_entry.setText(generated_password)
		self.repeat_password_entry.setText(generated_password)

	def toggle_visibility(self):
		if self.password_entry.echoMode() == QLineEdit.Password \
		and self.repeat_password_entry.echoMode() == QLineEdit.Password:
			self.password_entry.setEchoMode(QLineEdit.Normal)
			self.repeat_password_entry.setEchoMode(QLineEdit.Normal)
			self.visibility_button.setIcon(self.shown_icon)
		else:
			self.password_entry.setEchoMode(QLineEdit.Password)
			self.repeat_password_entry.setEchoMode(QLineEdit.Password)
			self.visibility_button.setIcon(self.hidden_icon)

	@staticmethod
	def generate_password(length):
		return "".join(secrets.choice(ascii_letters+digits+punctuation) for _ in range(length))