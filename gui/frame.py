from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QLabel,
    QGridLayout,
)

class Frame(QFrame):
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

    def edit(self):
        pass

    def delete(self):
        pass