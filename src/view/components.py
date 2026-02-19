from typing import List
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, 
    QSize,
)
from PyQt6.QtGui import QIcon

from src.utils.icon_loader import IconLoader
from src.utils.styles import Styles

class TitleLabel(QLabel):
    def __init__(self, text, fontSize = 45):
        super().__init__(text)
        self.setStyleSheet(Styles.title_label(fontSize))

class InfoLabel(QLabel):
    def __init__(self, text, fontSize = 12, bold = False, italic = False, color = 'black'):
        super().__init__(text)
        self.setStyleSheet(Styles.info_label(fontSize, bold, italic, color))

# Toggles among at least 2 options
class ToggleBox(QWidget):
    def __init__(self, options : List[str], mini = False):
        super().__init__()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setStyleSheet(Styles.toggle_box(mini))

        # Button layout
        button_layout = QHBoxLayout()
        if mini:
            button_layout.setSpacing(0)
        else:
            button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Button group
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        for i, text in enumerate(options):
            btn = QPushButton() if mini else QToolButton()
            btn.setText(' ' + text if mini else text)

            # Icon Group
            toggleable_icon = QIcon()
            toggleable_icon.addPixmap(IconLoader.get(text.lower() + '-dark').pixmap(64, 64), QIcon.Mode.Normal, QIcon.State.Off)
            toggleable_icon.addPixmap(IconLoader.get(text.lower() + '-light').pixmap(64, 64), QIcon.Mode.Normal, QIcon.State.On)

            btn.setIcon(toggleable_icon)
            if not mini:
                btn.setIconSize(btn.sizeHint() * 1.5)
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            button_layout.addWidget(btn)
            self.group.addButton(btn, i)

            if i == 0:
                btn.setChecked(True)

        layout.addLayout(button_layout)

class Card(QWidget):
    def __init__(self, id_name, fixed_size : QSize):
        super().__init__()
        self.setFixedSize(fixed_size)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName(id_name)
        self.setStyleSheet(Styles.card(id_name))
        self.setGraphicsEffect(Styles.card_shadow())