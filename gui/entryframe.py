import pyperclip
from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt

class Frame(QFrame):
    def __init__(self, title, username, password, url):
        super().__init__()

        self._title = title
        self._username = username
        self._password = password
        self._url = url
        self.title_label = QLabel(self._title, self)

        self.setStyleSheet("QFrame {border: 1px solid #7f7f7f;}")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.title_label)
        self.setLayout(self.layout)

    def edit(self):
        pass

    def delete(self):
        pass
