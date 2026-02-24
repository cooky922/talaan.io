from enum import Enum
from typing import Union
from PyQt6.QtWidgets import (
    QPushButton,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, 
    QSize,
    pyqtSignal, 
    pyqtSlot
)

from src.utils.constants import Constants
from src.utils.styles import Styles
from src.model.role import UserRole
from src.view.components import TitleLabel, InfoLabel, ToggleBox, Card

class RoleToggleArea(ToggleBox):
    def __init__(self):
        super().__init__(['Viewer', 'Admin'])

    def get_role(self) -> Union[UserRole, None]:
        checked_id = self.group.checkedId()
        if checked_id == 0:
            return UserRole.VIEWER
        elif checked_id == 1:
            return UserRole.ADMIN
        else:
            return None

class LoginForm(Card):
    def __init__(self, signal):
        super().__init__('LoginForm', size = QSize(250, 225))
        self.login_signal = signal

        login_layout = QVBoxLayout()
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(login_layout)

        self.role_toggle_area = RoleToggleArea()

        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet(Styles.action_button(back_color = Constants.LOGIN_BUTTON_COLOR))
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)

        # Layout
        login_layout.addWidget(TitleLabel('Select a Role', 24), alignment = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        login_layout.addWidget(self.role_toggle_area, alignment = Qt.AlignmentFlag.AlignCenter)
        login_layout.addStretch()
        login_layout.addWidget(self.login_button)

    def handle_login(self):
        selected_role = self.role_toggle_area.get_role()
        self.login_signal.emit(selected_role)

class LoginView(QWidget):
    login_signal = pyqtSignal(UserRole)

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('LoginView')
        self.setStyleSheet(Styles.page('LoginView'))

        # Layout 
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = TitleLabel('talaan.io')

        # Description
        desc = InfoLabel('Simple Student Information System', fontSize = 14)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card
        self.login_card = LoginForm(self.login_signal)

        # Structure 
        layout.addStretch()
        layout.addWidget(title, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        layout.addSpacing(20)
        layout.addWidget(self.login_card, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addStretch()