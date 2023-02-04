import sys

from PyQt5.QtWidgets import QApplication

from gui import MasterPromptWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterPromptWindow()
    window.show()
    sys.exit(app.exec_())