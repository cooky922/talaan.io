from typing import List
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QCompleter,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QToolButton,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, 
    QEasingCurve,
    QSize,
    QEvent,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QTimer
)
from PyQt6.QtGui import QIcon, QColor, QPen, QPainter, QCursor

from src.utils.icon_loader import IconLoader
from src.utils.font_loader import FontLoader
from src.utils.styles import Styles
from src.utils.constants import Constants

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
    def __init__(self, id_name, size : QSize):
        super().__init__()
        if id_name == 'TableCard':
            self.setMinimumSize(size)
        else:
            self.setFixedSize(size)
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
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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

class NoIconDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.icon = QIcon() 
        option.decorationSize = QSize(0, 0)

class SearchableComboBox(QComboBox):
    def __init__(self, items, placeholder=""):
        super().__init__()
        self.setEditable(True)
        self.addItems(items)
        
        # Inject Placeholder
        self.lineEdit().setPlaceholderText(placeholder)
        
        # Setup Search/Autocomplete
        if self.completer():
            self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.completer().popup().setStyleSheet(f"""
                QListView {{ 
                    background-color: white; 
                    border: 1px solid #CCCCCC; 
                    border-radius: 6px; 
                    outline: none; 
                    font-size: 11px; 
                }}
                QListView::item {{ 
                    padding: 8px 10px; 
                    color: #333333; 
                }}
                QListView::item:selected, QListView::item:hover {{ 
                    background-color: #f0f4e6; 
                    color: #333333; 
                    border-radius: 4px; /* Keeps the hover highlight inside the rounded box */
                }}
            """)

    def paintEvent(self, event):
        # 1. Let Qt draw the normal white box and the text first
        super().paintEvent(event)
        
        # 2. Grab our custom painter and turn on Anti-Aliasing!
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 3. Setup a crisp, rounded pen (match your dark gray text color)
        pen = QPen(QColor("#888888"), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # 4. Calculate the exact center of the right edge
        rect = self.rect()
        x = rect.width() - 15  # 15 pixels away from the right edge
        y = rect.height() // 2 # Exact vertical center
        
        # 5. Draw the perfectly crisp 'v' chevron mathematically!
        # Left wing
        painter.drawLine(x - 4, y - 2, x, y + 2)
        # Right wing
        painter.drawLine(x, y + 2, x + 4, y - 2)

class MessageBox(QMessageBox):
    def __init__(self, parent, title, message):
        msg = QMessageBox(parent)
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        # Apply the clean white theme and styled buttons
        self.setStyleSheet(f"""
            QMessageBox {{
                background-color: #ffffff;
            }}
            QLabel {{
                color: #333333;
                font-size: 12px;
                font-family: {FontLoader.get('default')}
            }}
        """)

    def exec(self):
        btn_yes = self.button(QMessageBox.StandardButton.Yes)
        if btn_yes:
            btn_yes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if self.icon() == QMessageBox.Icon.Warning:
                btn_yes.setStyleSheet(Styles.action_button(back_color=Constants.DANGER_COLOR, font_size=11))
            else:
                btn_yes.setStyleSheet(Styles.action_button(back_color=Constants.ACTIVE_BUTTON_COLOR, font_size=11))

        btn_cancel = self.button(QMessageBox.StandardButton.Cancel)
        if btn_cancel:
            btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_cancel.setStyleSheet(Styles.action_button(
                back_color=Constants.BUTTON_SECONDARY_COLOR, 
                text_color='#333333', 
                font_size=11, 
                bordered=True
            ))
            
        btn_ok = self.button(QMessageBox.StandardButton.Ok)
        if btn_ok:
            btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_ok.setStyleSheet(Styles.action_button(back_color=Constants.ACTIVE_BUTTON_COLOR, font_size=11))

        return super().exec()

class ToastNotification(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.container = QFrame(self)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(20, 10, 20, 10)
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 12px; background: transparent;")
        container_layout.addWidget(self.label)
        
        # Revert back to the graphics effect for opacity
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.anim_group = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        
        self.hide()

    def show_message(self, message, is_error  = False):
        self.timer.stop()
        if self.anim_group:
            self.anim_group.stop()
            
        self.label.setText(message)
        
        bg_color = "#ff4c4c" if is_error else "#333333"
        self.container.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border-radius: 6px; }}")
        
        self.adjustSize() 
        
        parent_widget = self.parentWidget()
        x = (parent_widget.width() - self.width()) // 2
        y = parent_widget.height() - self.height() - 40 
        
        start_pos = QPoint(x, y + 20)
        end_pos = QPoint(x, y)
        
        self.move(start_pos) 
        self.opacity_effect.setOpacity(0.0)
        
        self.show()
        self.raise_()
        
        self.anim_group = QParallelAnimationGroup()
        
        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(400)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic) 
        
        op_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        op_anim.setDuration(400)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(0.99)
        
        self.anim_group.addAnimation(pos_anim)
        self.anim_group.addAnimation(op_anim)
        self.anim_group.start()
        
        self.timer.start(2500)
        
    def hide_toast(self):
        if self.anim_group:
            self.anim_group.stop()
            
        self.anim_group = QParallelAnimationGroup()
        
        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(400)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(QPoint(self.pos().x(), self.pos().y() + 20))
        pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        
        op_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        op_anim.setDuration(400)
        op_anim.setStartValue(0.99)
        op_anim.setEndValue(0.0)
        
        self.anim_group.addAnimation(pos_anim)
        self.anim_group.addAnimation(op_anim)
        self.anim_group.finished.connect(self.hide) 
        self.anim_group.start()