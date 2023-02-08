

class AddDataWindow(QWidget):
	def __init__(self, parent, obj):
		super().__init__()
		self.setWindowTitle("Add entry")
		self.setMinimumSize(QSize(650, 450))

		self.parent = parent
		self.storage_handler = obj

		self.hidden_icon = QIcon("icons/hidden.png")
		self.shown_icon = QIcon("icons/shown.png")
		self.dice_icon = QIcon("icons/dice.png")

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

		self.generate_password_button = QPushButton(self)
		self.generate_password_button.setIcon(self.dice_icon)
		self.generate_password_button.setIconSize(QSize(19, 19))
		self.generate_password_button.setFixedSize(25, 25)

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

	def initUI(self):
		pass

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