from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, 
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon

from src.utils.font_loader import FontLoader
from src.utils.icon_loader import IconLoader
from src.view.ui.login_page import UserRole, LoginPage
from src.view.ui.working_page import WorkingPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Window
          | Qt.WindowType.CustomizeWindowHint 
          | Qt.WindowType.WindowTitleHint
          | Qt.WindowType.WindowCloseButtonHint
          | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setFixedSize(750, 450)
        self.setWindowTitle('talaan.io')
        icon_path = Path(__file__).parent.parent.parent.parent / 'assets' / 'images' / 'icons' / 'app-logo.ico'
        self.setWindowIcon(QIcon(str(icon_path)))

        # Load fonts
        FontLoader.load()
        IconLoader.load()

        # Structure
        self.view = QStackedWidget()
        self.setCentralWidget(self.view)

        self.login_page = LoginPage()
        self.working_page = WorkingPage()

        self.view.addWidget(self.login_page)
        self.view.addWidget(self.working_page)

        self.login_page.login_signal.connect(self.on_login)
        self.working_page.logout_signal.connect(self.on_logout)

    @pyqtSlot(UserRole)
    def on_login(self, role : UserRole):
        self.working_page.set_role(role)
        self.view.setCurrentIndex(1)

    @pyqtSlot()
    def on_logout(self):
        self.view.setCurrentIndex(0)