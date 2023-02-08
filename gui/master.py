

class MasterWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.master_handler = MasterManip()

	def initUI(self):
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

		self.config_label()

		self.setLayout(master_grid)
		self.setWindowTitle("Authentication")
		self.setMinimumSize(QSize(650, 400))

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