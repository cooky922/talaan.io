import sys
from PyQt6.QtWidgets import QApplication

from src.model.database import StudentDirectory, ProgramDirectory, CollegeDirectory
from src.view.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    print('before initialization')
    window = MainWindow()
    print('initialization done')
    window.show()
    ret = app.exec()
    StudentDirectory.save()
    ProgramDirectory.save()
    CollegeDirectory.save()
    sys.exit(ret)

if __name__ == '__main__':
    main()