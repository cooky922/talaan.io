from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, 
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon

from src.model.role import UserRole
from src.utils.font_loader import FontLoader
from src.utils.icon_loader import IconLoader
from src.view.ui.login_view import LoginView
from src.view.ui.working_view import WorkingView

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Window
          | Qt.WindowType.CustomizeWindowHint 
          | Qt.WindowType.WindowTitleHint
          | Qt.WindowType.WindowCloseButtonHint
          | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setMinimumSize(800, 450)
        self.setWindowTitle('talaan.io - Simple Student Information System')
        icon_path = Path(__file__).parent.parent.parent.parent / 'assets' / 'images' / 'icons' / 'app-logo.ico'
        self.setWindowIcon(QIcon(str(icon_path)))

        # Load fonts
        FontLoader.load()
        FontLoader.add_default(app.font().family())
        IconLoader.load()

        # Structure
        self.container = QStackedWidget()
        self.setCentralWidget(self.container)

        print('initializing login page')
        self.login_view = LoginView()

        print('initializing working page')
        self.working_view = WorkingView()

        self.container.addWidget(self.login_view)
        self.container.addWidget(self.working_view)

        self.login_view.login_signal.connect(self.on_login)
        self.working_view.logout_signal.connect(self.on_logout)

    @pyqtSlot(UserRole)
    def on_login(self, role : UserRole):
        self.working_view.set_role(role)
        self.container.setCurrentIndex(1)

    @pyqtSlot()
    def on_logout(self):
        self.working_view.set_default()
        self.container.setCurrentIndex(0)