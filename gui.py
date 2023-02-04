import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import manip

class MasterPromptWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Authentication")
		self.setMinimumSize(QSize(650, 450))

		if not os.path.exists("database"):
			os.mkdir("database")

		self.master_label = QLabel(self)
		self.master_entry = QLineEdit(self)
		self.master_entry.setEchoMode(QLineEdit.Password)
		self.visibility_button = QPushButton("Show", self)
		self.auth_button = QPushButton("Auth", self)

		self.auth_button.clicked.connect(self.auth_user)
		self.visibility_button.clicked.connect(self.toggle_visibility)

		master_grid = QGridLayout()
		master_grid.addWidget(self.master_label, 0, 0)
		master_grid.addWidget(self.master_entry, 1, 0)
		master_grid.addWidget(self.visibility_button, 1, 1)
		master_grid.addWidget(self.auth_button, 2, 0, 1, 2)

		self.setLayout(master_grid)
		master_grid.setAlignment(Qt.AlignCenter)
		self.config_label()

	def auth_user(self):
		self.window = StorageWindow()
		master_pw = self.master_entry.text()
		self.master_entry.clear()

		if not manip.master_file_exists():
			manip.write_password(master_pw.encode())
			manip.create_storage()
			self.close()
			self.window.show()
		else:
			if manip.verify_password(master_pw.encode()):
				self.close()
				self.window.show()
			else:
				QMessageBox.critical(self, "Error!", "Sorry, the password you entered is incorrect or the file you are trying to access is either corrupt or doesn't exist.")

	def toggle_visibility(self):
		if self.master_entry.echoMode() == QLineEdit.Password:
			self.master_entry.setEchoMode(QLineEdit.Normal)
			self.visibility_button.setText("Hide")
		else:
			self.master_entry.setEchoMode(QLineEdit.Password)
			self.visibility_button.setText("Show")

	def config_label(self):
		if not manip.master_file_exists():
			self.master_label.setText("Create a master password:")
		else:
			self.master_label.setText("Enter master password:")

class StorageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Storage")
        self.setMinimumSize(QSize(750, 500))
        self.data_window = AddDataWindow()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        button = QPushButton("Add entry", central_widget)
        self.search_button = QPushButton("Search entry", central_widget)
        self.search_entry = QLineEdit(central_widget)
        self.search_entry.setVisible(False)
        self.combo = QComboBox(central_widget)

        self.combo.addItem("Search by: Title")
        self.combo.addItem("Search by: URL")
        self.combo.addItem("Search by: Username")
        self.combo.setVisible(False)

        button.clicked.connect(self.data_window.show)

        self.storage_grid = QGridLayout(central_widget)
        self.storage_grid.addWidget(button, 0, 0)
        self.storage_grid.addWidget(self.search_button, 0, 1)

        self.search_button.clicked.connect(self.toggle_widgets)

        self.storage_grid.setAlignment(Qt.AlignCenter)

    def toggle_widgets(self):
    	if self.search_entry.isVisible() and self.combo.isVisible():
    		self.search_entry.setVisible(False)
    		self.combo.setVisible(False)
    	else:
    		self.search_entry.setVisible(True)
    		self.combo.setVisible(True)
    		self.storage_grid.addWidget(self.combo, 1, 0)
    		self.storage_grid.addWidget(self.search_entry, 1, 1)


class AddDataWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Add entry")
		self.setMinimumSize(QSize(650, 450))

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

		self.generate_password_button = QPushButton("Generate password", self)
		self.visibility_button = QPushButton("Show", self)
		self.spin_box = QSpinBox(self)
		self.spin_box.setRange(1, 48)
		self.spin_box.setValue(16)

		self.url_label = QLabel("URL:", self)
		self.url_entry = QLineEdit(self)

		self.submit_button = QPushButton("Add", self)

		self.generate_password_button.clicked.connect(self.generate_password)
		self.visibility_button.clicked.connect(self.toggle_visibility)
		self.submit_button.clicked.connect(self.send_entry)

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

	def generate_password(self):
		length = self.spin_box.value()
		generated_password = manip.generate_password(length)
		self.password_entry.setText(generated_password)
		self.repeat_password_entry.setText(generated_password)

	def toggle_visibility(self):
		if self.password_entry.echoMode() == QLineEdit.Password and self.repeat_password_entry.echoMode() == QLineEdit.Password:
			self.password_entry.setEchoMode(QLineEdit.Normal)
			self.repeat_password_entry.setEchoMode(QLineEdit.Normal)
			self.visibility_button.setText("Hide")
		else:
			self.password_entry.setEchoMode(QLineEdit.Password)
			self.repeat_password_entry.setEchoMode(QLineEdit.Password)
			self.visibility_button.setText("Show")

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

	def send_entry(self):
		if self.validate_entry():
			title = self.title_entry.text()
			username = self.username_entry.text()
			password = self.password_entry.text()
			url = self.url_entry.text()
			data = manip.pack_data(title=title,
				username=username,
				password=password,
				url=url)
			manip.insert_entry(data=data)
			self.title_entry.clear()
			self.username_entry.clear()
			self.password_entry.clear()
			self.repeat_password_entry.clear()
			self.url_entry.clear()
			self.close()
