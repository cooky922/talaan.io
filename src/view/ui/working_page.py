from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTableView,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt, 
    QEvent,
    QSize,
    QAbstractTableModel, 
    QRegularExpression,
    QSortFilterProxyModel, 
    pyqtSignal, 
    pyqtSlot
)
from PyQt6.QtGui import QIcon, QColor 

from src.model.database import StudentDatabase, ProgramDatabase, CollegeDatabase
from src.utils.constants import Constants
from src.utils.styles import Styles
from src.utils.icon_loader import IconLoader

from src.view.components import TitleLabel, InfoLabel, ToggleBox, Card
from src.view.ui.login_page import UserRole

class DirectoryToggleBox(ToggleBox):
    def __init__(self):
        super().__init__(['Students', 'Programs', 'Colleges'], mini = True)

class Header(QWidget):
    def __init__(self, signal):
        super().__init__()
        self.logout_signal = signal

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('Header')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(Styles.header())

        # Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Elements
        self.title_label = TitleLabel('talaan.io', fontSize = 24)
        self.role_label = InfoLabel('Viewer', fontSize = 12, bold = True)

        self.directory_toggle_box = DirectoryToggleBox()

        self.logout_button = QPushButton('Logout')
        self.logout_button.setStyleSheet(Styles.action_button(back_color = Constants.LOGOUT_BUTTON_COLOR, font_size = 12))
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout_signal)

        # Structure 
        layout.addSpacing(10)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.directory_toggle_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.role_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(5)
        layout.addWidget(self.logout_button, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(10)

class TableModel(QAbstractTableModel):
    def __init__(self, db):
        super().__init__()
        self._db = db
        self._headers = db.get_columns()

    def set_database(self, db):
        self.beginResetModel()
        self._db = db 
        self._headers = db.get_columns()
        self.endResetModel()
    
    def rowCount(self, parent = None):
        return self._db.get_count()
    
    def columnCount(self, parent = None):
        return len(self._headers)
    
    def data(self, index, role = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            key = self._headers[col]
            return self._db.get_record(index = row)[key]
        return None
    
    def headerData(self, section, orientation, role = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._db.get_column_display_name(self._headers[section])
        return None
    
class RowHoverDelegate(QStyledItemDelegate):
    def __init__(self, table):
        super().__init__(table)
        self.table = table
        self.hovered_row = -1

        # 1. Force the table to track the mouse without needing to click
        self.table.setMouseTracking(True)
        
        # 2. Update the hovered row whenever the mouse enters a new cell
        self.table.entered.connect(self.on_entered)
        
        # 3. Listen for when the mouse leaves the table completely
        self.table.viewport().installEventFilter(self)

    def on_entered(self, index):
        self.hovered_row = index.row()
        self.table.viewport().update() # Force the table to visually refresh

    def eventFilter(self, obj, event):
        # Clear the highlight when the mouse leaves the table
        if obj == self.table.viewport() and event.type() == QEvent.Type.Leave:
            self.hovered_row = -1
            self.table.viewport().update()
        return super().eventFilter(obj, event)

    def paint(self, painter, option, index):
        # If this cell is part of the row currently being hovered...
        if index.row() == self.hovered_row:
            painter.fillRect(option.rect, QColor(0, 0, 0, 26))

        # Tell Qt to draw the normal text/content over our new background
        super().paint(painter, option, index)

class TableHeader(QHeaderView):
    def paintSection(self, painter, rect, logicalIndex):
        # 1. Let Qt draw the normal header first (Text, Background, and our new SVG Arrows)
        super().paintSection(painter, rect, logicalIndex)

        # 2. Draw our custom "floating" separator!
        # We skip the very last column so there isn't a line at the far right edge.
        if logicalIndex < self.count() - 1:
            painter.save()
            pen = painter.pen()
            pen.setColor(QColor("#dddddd")) # Light gray line
            pen.setWidth(2)
            painter.setPen(pen)

            x = rect.right()
            y_top = rect.top() + 15
            y_bottom = rect.bottom() - 15
            
            # Draw the line
            painter.drawLine(x, y_top, x, y_bottom)
            painter.restore()

class Table(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(650, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        # Table
        self.table_model = TableModel(StudentDatabase)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.setFilterKeyColumn(-1)
        
        self.table = QTableView()

        self.hover_delegate = RowHoverDelegate(self.table)
        custom_header = TableHeader(Qt.Orientation.Horizontal, self.table)
        self.table.setHorizontalHeader(custom_header)

        self.table.setItemDelegate(self.hover_delegate)
        self.table.setStyleSheet(Styles.table())
        self.table.setModel(self.proxy_model)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setSortingEnabled(True)
        custom_header.setSectionsClickable(True)
        custom_header.setSortIndicatorShown(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

        # Layout
        layout.addWidget(self.table)

        self.table.resizeColumnsToContents()
        custom_header.setStretchLastSection(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

class ToolBar(QWidget):
    def __init__(self, handle_text_change):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.setLayout(layout)

        # Component
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search')
        self.search_bar.setStyleSheet(Styles.search_bar())
        self.search_bar.setFixedWidth(300)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(handle_text_change)
        self.search_bar.addAction(IconLoader.get('search-dark'), QLineEdit.ActionPosition.LeadingPosition)

        # Structure
        layout.addSpacing(15)
        layout.addWidget(self.search_bar, alignment = Qt.AlignmentFlag.AlignLeft)

class FootBar(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.setLayout(layout)

        # Component
        self.entries_label = InfoLabel('Results', color = Constants.TEXT_SECONDARY_COLOR)

        # Structure
        layout.addSpacing(15)
        layout.addWidget(self.entries_label, alignment = Qt.AlignmentFlag.AlignLeft)

class TableCard(Card):
    def __init__(self):
        super().__init__('TableCard', fixed_size = QSize(700, 350))

        table_layout = QVBoxLayout()
        table_layout.setSpacing(4)
        table_layout.setContentsMargins(5, 5, 5, 5)

        self.setLayout(table_layout)

        # Components
        self.table_view = Table()
        self.table_view.table_model.modelReset.connect(self.update_entry_count)
        self.tool_bar = ToolBar(self.search_table)
        self.foot_bar = FootBar()
        self.update_entry_count()

        # Layout
        table_layout.addSpacing(10)
        table_layout.addWidget(self.tool_bar, alignment=Qt.AlignmentFlag.AlignLeft)
        table_layout.addWidget(self.table_view)
        table_layout.addWidget(self.foot_bar)
        table_layout.addSpacing(10)

    def update_entry_count(self):
        visible_count = self.table_view.proxy_model.rowCount()
        total_count = self.table_view.table_model.rowCount()
        if visible_count == total_count:
            self.foot_bar.entries_label.setText(f'Showing all {total_count} entries')
        else:
            self.foot_bar.entries_label.setText(f'Showing {visible_count} of {total_count} entries')

    def search_table(self, text):
        regex = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.table_view.proxy_model.setFilterRegularExpression(regex)
        self.update_entry_count()

    def switch_table(self, button_id):
        # 1. Reset the hover state safely (This won't crash anymore!)
        self.table_view.table.setSortingEnabled(False)
        self.table_view.hover_delegate.hovered_row = -1
        self.tool_bar.search_bar.blockSignals(True)
        self.tool_bar.search_bar.clear()
        self.tool_bar.search_bar.blockSignals(False)
        self.table_view.proxy_model.setFilterRegularExpression('')
        match button_id:
            case 0: 
                self.table_view.table_model.set_database(StudentDatabase)
            case 1:
                self.table_view.table_model.set_database(ProgramDatabase)
            case 2:
                self.table_view.table_model.set_database(CollegeDatabase)
        self.table_view.table.setSortingEnabled(True)
        self.table_view.table.resizeColumnsToContents()
        self.update_entry_count()

class WorkingPage(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('WorkingPage')
        self.setStyleSheet(Styles.page('WorkingPage'))

        # Role
        self.role = None

        # Layout 
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Elements
        self.header = Header(self.logout_signal)
        self.table_card = TableCard()
        self.header.directory_toggle_box.group.idClicked.connect(self.table_card.switch_table)

        # Structure
        layout.addWidget(self.header)
        layout.addSpacing(10)
        layout.addWidget(self.table_card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def set_role(self, role : UserRole):
        self.role = role
        self.header.role_label.setText(role.value)