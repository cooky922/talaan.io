import sys
from PyQt6.QtWidgets import QApplication

from src.view.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    print('before initialization')
    window = MainWindow()
    print('initialization done')
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()