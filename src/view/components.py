from typing import List
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyledItemDelegate,
    QToolButton,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, 
    QSize,
    QEvent
)
from PyQt6.QtGui import QIcon, QColor, QPen

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

class RowHoverDelegate(QStyledItemDelegate):
    def __init__(self, table):
        super().__init__(table)
        self.table = table
        self.hovered_row = -1

        self.table.setMouseTracking(True)
        self.table.entered.connect(self.on_entered)
        self.table.viewport().installEventFilter(self)

    def on_entered(self, index):
        self.hovered_row = index.row()
        self.table.viewport().update()

    def eventFilter(self, obj, event):
        if obj == self.table.viewport() and event.type() == QEvent.Type.Leave:
            self.hovered_row = -1
            self.table.viewport().update()
        return super().eventFilter(obj, event)

    def paint(self, painter, option, index):
        if index.row() == self.hovered_row:
            painter.fillRect(option.rect, QColor(0, 0, 0, 26))
        super().paint(painter, option, index)

class TableHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        logical_index = self.logicalIndexAt(event.pos())
        if logical_index == -1:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            return
        x = event.pos().x()
        left_edge = self.sectionViewportPosition(logical_index)
        right_edge = left_edge + self.sectionSize(logical_index)
        
        on_left_divider = (x - left_edge) <= 5 and logical_index > 0
        on_right_divider = (right_edge - x) <= 5 and logical_index < self.count() - 1
        
        if on_left_divider or on_right_divider:
            self.viewport().setCursor(Qt.CursorShape.SplitHCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        painter.save()

        if logicalIndex < self.count() - 1:
            pen = painter.pen()
            pen.setColor(QColor('#dddddd')) 
            pen.setWidth(2)
            painter.setPen(pen)

            x = rect.right()
            y_top = rect.top() + 15
            y_bottom = rect.bottom() - 15
            
            painter.drawLine(x, y_top, x, y_bottom)
        
        if self.isSortIndicatorShown() and self.sortIndicatorSection() == logicalIndex:
            arrow_pen = QPen(QColor('#888888'), 1.5) 
            arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(arrow_pen)

            center_y = rect.top() + (rect.height() // 2)
            arrow_x = rect.right() - 18 

            # Smaller chevron math: Width = 8px (x to x+4 to x+8), Height = 4px
            if self.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder:
                painter.drawLine(arrow_x, center_y + 2, arrow_x + 4, center_y - 2)
                painter.drawLine(arrow_x + 4, center_y - 2, arrow_x + 8, center_y + 2)
            else:
                painter.drawLine(arrow_x, center_y - 2, arrow_x + 4, center_y + 2)
                painter.drawLine(arrow_x + 4, center_y + 2, arrow_x + 8, center_y - 2)

        painter.restore()