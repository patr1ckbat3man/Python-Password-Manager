import sys

from PyQt5.QtWidgets import QApplication

from gui import MasterWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec_())