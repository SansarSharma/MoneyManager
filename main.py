# File: main.py
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from managers.screen_manager import ScreenManager

def main():
    app = QApplication(sys.argv)

    QMessageBox.information(
        None,
        "Welcome",
        "Welcome to Money Manager!\n\n"
        "• Continue Without File: start a fresh session.\n"
        "• Upload Excel File: load your existing template.\n"
        "• Download Template: save a blank template to fill later."
    )

    sm = ScreenManager()
    sm.show_welcome()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
