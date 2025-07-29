import sys
from PySide6.QtWidgets import QApplication
from geminiteacher.gui.main_window import MainWindow

def main():
    """The main entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 