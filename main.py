import sys

from PyQt5.QtWidgets import QApplication

from gui import MasterWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    password_manager = MasterWindow()
    sys.exit(app.exec_())