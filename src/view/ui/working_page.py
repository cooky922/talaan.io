import math
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableView,
    QWidget, 
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt,
    QSize,
    QAbstractTableModel, 
    pyqtSignal, 
    QTimer
)
from PyQt6.QtGui import QColor, QCursor

from src.model.database import StudentDirectory, ProgramDirectory, CollegeDirectory, Paged, Sorted
from src.utils.constants import Constants
from src.utils.styles import Styles
from src.utils.icon_loader import IconLoader

from src.view.components import (
    TitleLabel, 
    InfoLabel, 
    ToggleBox, 
    Card,
    RowHoverDelegate,
    SearchableComboBox,
    TableHeader
)
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

class RecordDialog(QDialog):
    def __init__(self, current_directory, record=None, parent=None):
        super().__init__(parent)
        self.current_directory = current_directory
        self.record = record
        self.is_edit_mode = record is not None 
        
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        if self.current_directory == StudentDirectory:
            self.setFixedWidth(350)
        elif self.current_directory == ProgramDirectory:
            self.setFixedWidth(400)
        elif self.current_directory == CollegeDirectory:
            self.setFixedWidth(400)
            
        self.setObjectName("RecordDialog")
        self.setStyleSheet("""
            QDialog#RecordDialog { background-color: #ffffff; }
            QLabel { color: #333333; }
        """)
        
        title_text = "Edit Record" if self.is_edit_mode else "Add Record"
        if self.current_directory == StudentDirectory: title_text = title_text.replace("Record", "Student")
        elif self.current_directory == ProgramDirectory: title_text = title_text.replace("Record", "Program")
        elif self.current_directory == CollegeDirectory: title_text = title_text.replace("Record", "College")
        self.setWindowTitle(title_text)
        
        self.inputs = {}
        self.setup_ui()
        self.populate_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        
        columns = self.current_directory.get_columns()
        primary_key = self.current_directory._db.primary_key
        
        row_idx = 0
        col_idx = 0
        
        for col_name in columns:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(5)
            
            label_text = self.current_directory.get_column_display_name(col_name)
            
            lbl = QLabel(label_text.upper())
            lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #555555;")
            field_layout.addWidget(lbl)
            
            # Pass the label_text to create placeholders!
            input_widget = self.create_input_widget(col_name, label_text)
            
            if self.is_edit_mode and col_name == primary_key:
                if isinstance(input_widget, QComboBox):
                    input_widget.setEnabled(False)
                else:
                    input_widget.setReadOnly(True)
                
                # Apply the dashed border, gray background, and Forbidden Cursor
                disabled_css = """
                    background-color: #f7f7f7 !important;
                    color: #aaaaaa !important;
                    border: 1px dashed #cccccc !important;
                """
                input_widget.setStyleSheet(input_widget.styleSheet() + f" QLineEdit {{ {disabled_css} }} QComboBox {{ {disabled_css} }}")
                input_widget.setCursor(Qt.CursorShape.ForbiddenCursor)

            field_layout.addWidget(input_widget)
            self.inputs[col_name] = input_widget
            
            if col_name in ['first_name', 'last_name', 'year', 'gender']:
                self.grid_layout.addLayout(field_layout, row_idx, col_idx)
                col_idx += 1
                if col_idx > 1:
                    col_idx = 0
                    row_idx += 1
            else:
                if col_idx == 1: 
                    row_idx += 1
                    col_idx = 0
                self.grid_layout.addLayout(field_layout, row_idx, 0, 1, 2)
                row_idx += 1

        main_layout.addLayout(self.grid_layout)
        main_layout.addSpacing(10)

        footer_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color: white; border: 1px solid #CCCCCC; border-radius: 4px; padding: 6px 15px; color: #555555; }
            QPushButton:hover { background-color: #F5F5F5; }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        action_text = "Save" if self.is_edit_mode else "Add"
        self.btn_action = QPushButton(action_text)
        self.btn_action.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_action.setStyleSheet("""
            QPushButton { background-color: #8fae44; border: none; border-radius: 4px; padding: 6px 20px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #7a9638; }
        """)
        self.btn_action.clicked.connect(self.accept)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addWidget(self.btn_action)
        main_layout.addLayout(footer_layout)

        self.adjustSize()
        self.setFixedHeight(self.height())

    def create_input_widget(self, col_name, label_text):
        base_style = """
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            background-color: white;
            color: #333333;
            font-size: 11px;
        """
        
        interactive_states = """
            :hover { border: 1px solid #8fae44; }
            :focus { border: 1.5px solid #8fae44; background-color: #fcfff5; }
        """

        # Notice how we completely killed the down-arrow image here!
        combo_style = f"""
            QComboBox {{ {base_style} padding: 6px 10px; }}
            QComboBox{interactive_states}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right; width: 30px; border-left: none;
            }}
            QComboBox::down-arrow {{
                image: none; background: none; border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: white; color: #333333; border: 1px solid #CCCCCC;
                selection-background-color: #f0f4e6; selection-color: #333333; outline: none;
            }}
            QLineEdit {{
                background: transparent; border: none; padding: 0px; color: #333333; font-size: 11px;
            }}
            QLineEdit::placeholder {{ color: #bbbbbb; }}
        """

        placeholder = f"Enter {label_text.lower()}"
        select_placeholder = f"Select {label_text.lower()}"

        if col_name == 'gender': 
            cb = SearchableComboBox(['Male', 'Female', 'Other'], select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        elif col_name == 'year': 
            cb = SearchableComboBox(['1', '2', '3', '4'], select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        elif col_name == 'program_code' and self.current_directory == StudentDirectory:
            cb = SearchableComboBox([""] + ProgramDirectory.get_keys(), select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        elif col_name == 'college_code' and self.current_directory == ProgramDirectory:
            cb = SearchableComboBox([""] + CollegeDirectory.get_keys(), select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        else:
            le = QLineEdit()
            le.setPlaceholderText(placeholder)
            le_style = f"QLineEdit {{ {base_style} padding: 6px 10px; }} QLineEdit{interactive_states} QLineEdit::placeholder {{ color: #bbbbbb; }}"
            le.setStyleSheet(le_style)
            return le

    def populate_data(self):
        if not self.is_edit_mode: return
        for col_name, widget in self.inputs.items():
            val = str(self.record.get(col_name, ""))
            if isinstance(widget, QComboBox): widget.setCurrentText(val)
            elif isinstance(widget, QLineEdit): widget.setText(val)

    def get_data(self) -> dict:
        data = {}
        for col_name, widget in self.inputs.items():
            val = None
            if isinstance(widget, QComboBox):
                val = widget.currentText()
            elif isinstance(widget, QLineEdit):
                val = widget.text()
            else:
                val = ''
            data[col_name] = val
        return data
    
        
class TableModel(QAbstractTableModel):
    def __init__(self, db):
        super().__init__()
        self._db = db
        self._headers = db.get_columns()
        self._data = [] # This data holds only the exact rows for the current page

    def set_database(self, db):
        self.beginResetModel()
        self._db = db 
        self._headers = db.get_columns()
        self._data = [] 
        self.endResetModel()

    def set_data(self, data: list[dict]):
        # Injects the new page of data from the database directly into the view
        self.beginResetModel()
        self._data = data
        self.endResetModel()
    
    def rowCount(self, parent = None):
        return len(self._data)
    
    def columnCount(self, parent = None):
        return len(self._headers)
    
    def data(self, index, role = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            key = self._headers[col]
            # Safely fetch the data from the current chunk
            return str(self._data[row].get(key, ''))
        return None
    
    def headerData(self, section, orientation, role = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._db.get_column_display_name(self._headers[section]).upper()
        return None        

class Table(QWidget):
    def __init__(self):
        super().__init__()
        
        self.resize(650, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        self.table_model = TableModel(StudentDirectory)
        self.table = QTableView()

        self.hover_delegate = RowHoverDelegate(self.table)
        self.custom_header = TableHeader(Qt.Orientation.Horizontal, self.table)
        self.table.setHorizontalHeader(self.custom_header)

        self.table.setItemDelegate(self.hover_delegate)
        self.table.setStyleSheet(Styles.table())

        self.table.setModel(self.table_model)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.custom_header.setSectionsClickable(True)
        self.custom_header.setSortIndicatorShown(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

        # Layout
        layout.addWidget(self.table)

        self.custom_header.setStretchLastSection(True)


class ToolBar(QWidget):
    edit_mode_toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_edit_mode = False
        
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
        self.search_bar.addAction(IconLoader.get('search-dark'), QLineEdit.ActionPosition.LeadingPosition)

        self.add_button = QPushButton(' Add')
        self.add_button.setIcon(IconLoader.get('add-light'))
        self.add_button.setStyleSheet(Styles.action_button(back_color = Constants.ACTIVE_BUTTON_COLOR, font_size = 12))
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.hide()

        self.edit_button = QPushButton(' Edit')
        self.edit_button.setIcon(IconLoader.get('edit-light'))
        self.edit_button.setStyleSheet(Styles.action_button(back_color = Constants.ACTIVE_BUTTON_COLOR, font_size = 12))
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.edit_button.clicked.connect(self.toggle_mode)

        # Structure
        layout.addSpacing(15)
        layout.addWidget(self.search_bar)
        layout.addStretch()
        layout.addWidget(self.add_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.edit_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(15)

    def toggle_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.setText(' Done')
            self.edit_button.setIcon(IconLoader.get('done-dark'))
            self.edit_button.setStyleSheet(Styles.action_button(back_color = "#CCCCCC", font_size = 12, text_color = '#333333'))
            self.add_button.show()
        else:
            self.edit_button.setText(' Edit')
            self.edit_button.setIcon(IconLoader.get('edit-light'))
            self.edit_button.setStyleSheet(Styles.action_button(back_color = Constants.ACTIVE_BUTTON_COLOR, font_size = 12))
            self.add_button.hide()
        self.edit_mode_toggled.emit(self.is_edit_mode)


class PaginationControl(QWidget):
    # Custom signal that alerts the main page to fetch new data chunks
    page_changed = pyqtSignal(int)

    def __init__(self, items_per_page=100):
        super().__init__()
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_rows = 0

        self.setStyleSheet(Styles.pagination_control())
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_entries = InfoLabel("Page 1 out of 1", color = Constants.TEXT_SECONDARY_COLOR)
        # self.lbl_entries.setStyleSheet("color: #888888; font-weight: bold; font-size: 13px;")

        self.page_btn_layout = QHBoxLayout()
        self.page_btn_layout.setSpacing(2)

        self.main_layout.addWidget(self.lbl_entries)
        self.main_layout.addStretch() 
        self.main_layout.addLayout(self.page_btn_layout)

    def update_data_stats(self, total_rows):
        # Called by 'TableCard' when the database returns the fresh count
        self.total_rows = total_rows
        total_pages = math.ceil(total_rows / self.items_per_page)
        if total_pages == 0: total_pages = 1
        
        # Failsafe bounds check
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
            
        self.redraw_ui()
        self.setVisible(total_pages > 1)

    def go_to_page(self, page_index):
        self.current_page = page_index
        # Signal the TableCard to ask the database for this page
        self.page_changed.emit(self.current_page)

    def redraw_ui(self):
        total_pages = math.ceil(self.total_rows / self.items_per_page)
        if total_pages == 0: total_pages = 1

        self.lbl_entries.setText(f"Page {self.current_page + 1} out of {total_pages}")

        for i in reversed(range(self.page_btn_layout.count())):
            item = self.page_btn_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        btn_prev = QPushButton()
        btn_prev.setIcon(IconLoader.get('arrow-backward-gray'))
        btn_prev.setObjectName("NavArrow")
        btn_prev.setFixedSize(25, 25)
        btn_prev.setEnabled(self.current_page > 0)
        btn_prev.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
        self.page_btn_layout.addWidget(btn_prev)

        if total_pages <= 5:
            for p in range(total_pages): self._add_page_btn(p)
        else:
            if self.current_page < 3:
                for p in range(4): self._add_page_btn(p)
                self._add_dots()
                self._add_page_btn(total_pages - 1)
            elif self.current_page > total_pages - 4:
                self._add_page_btn(0)
                self._add_dots()
                for p in range(total_pages - 4, total_pages): self._add_page_btn(p)
            else:
                self._add_page_btn(0)
                self._add_dots()
                self._add_page_btn(self.current_page - 1)
                self._add_page_btn(self.current_page)
                self._add_page_btn(self.current_page + 1)
                self._add_dots()
                self._add_page_btn(total_pages - 1)

        btn_next = QPushButton()
        btn_next.setIcon(IconLoader.get('arrow-forward-gray'))
        btn_next.setObjectName('NavArrow')
        btn_next.setFixedSize(25, 25)
        btn_next.setEnabled(self.current_page < total_pages - 1)
        btn_next.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        self.page_btn_layout.addWidget(btn_next)

    def _add_page_btn(self, page_num):
        btn = QPushButton(str(page_num + 1))
        btn.setObjectName('PageButton')
        btn.setFixedSize(25, 25)
        btn.setProperty('active', page_num == self.current_page)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        btn.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_btn_layout.addWidget(btn)

    def _add_dots(self):
        lbl = InfoLabel('...', color = Constants.TEXT_SECONDARY_COLOR)
        lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.page_btn_layout.addWidget(lbl)


class FootBar(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.setLayout(layout)

        # Component
        self.entries_label = InfoLabel('Results', color = Constants.TEXT_SECONDARY_COLOR)
        
        # Initialized independently without proxy/table references
        self.pagination = PaginationControl(items_per_page = 100)

        # Structure
        layout.addSpacing(15)
        layout.addWidget(self.entries_label, alignment = Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.pagination)
        layout.addSpacing(15)

class TableCard(Card):
    def __init__(self):
        super().__init__('TableCard', fixed_size = QSize(700, 350))

        table_layout = QVBoxLayout()
        table_layout.setSpacing(4)
        table_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(table_layout)

        # State Tracking
        self.current_db = StudentDirectory
        self.search_text = ""
        self.sort_state = None
        self.current_page = 0
        self.items_per_page = 100

        # Components
        self.table_view = Table()
        self.tool_bar = ToolBar()
        self.foot_bar = FootBar()

        # Wire Up the Debounce Search Timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(10)
        self.search_timer.timeout.connect(self.on_search_triggered)
        self.tool_bar.search_bar.textChanged.connect(self.search_timer.start)

        # Wire Up Pagination & Sorting Signals
        self.tool_bar.add_button.clicked.connect(self.open_add_dialog)
        self.table_view.custom_header.sortIndicatorChanged.connect(self.on_sort_changed)
        self.table_view.table.clicked.connect(self.on_row_clicked)
        self.foot_bar.pagination.page_changed.connect(self.on_page_changed)

        # Layout
        table_layout.addSpacing(10)
        table_layout.addWidget(self.tool_bar)
        table_layout.addWidget(self.table_view)
        table_layout.addWidget(self.foot_bar)
        table_layout.addSpacing(10)

        # Booting
        self.table_view.custom_header.blockSignals(True)
        self.table_view.custom_header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.table_view.custom_header.blockSignals(False)

        col_name = self.current_db.get_columns()[0]
        self.sort_state = Sorted.By(col_name, ascending = True)
        self.fetch_data()

    def on_search_triggered(self):
        self.search_text = self.tool_bar.search_bar.text()
        self.current_page = 0
        self.foot_bar.pagination.current_page = 0
        self.fetch_data()

    def on_page_changed(self, page_index):
        self.current_page = page_index
        self.fetch_data()

    # triggered when a user clicks a row in the table
    def on_row_clicked(self, index):
        # if the toolbar is not in edit mode, do nothing
        if not self.tool_bar.is_edit_mode:
            return
        record = self.table_view.table_model._data[index.row()]
        primary_key = self.current_db._db.primary_key
        key_value = record[primary_key]

        dialog = RecordDialog(self.current_db, record = record, parent = self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                self.current_db.update_record(new_data, key = key_value)
                self.fetch_data()
            except Exception as e:
                self.show_custom_message('Error', f'Failed to update record;\n{str(e)}', is_error = True)

    def open_add_dialog(self):
        dialog = RecordDialog(self.current_db, record = None, parent = self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                self.current_db.add_record(new_data)
                self.fetch_data()
            except Exception as e:
                self.show_custom_message('Error', f'Failed to add record;\n{str(e)}', is_error = True)

    def on_sort_changed(self, column_index, order):
        col_name = self.current_db.get_columns()[column_index]
        ascending = order == Qt.SortOrder.AscendingOrder
        self.sort_state = Sorted.By(col_name, ascending)
        
        self.current_page = 0
        self.foot_bar.pagination.current_page = 0
        self.fetch_data()

    def switch_table(self, button_id):
        self.table_view.table.setSortingEnabled(False)
        self.table_view.hover_delegate.hovered_row = -1
        
        self.tool_bar.search_bar.blockSignals(True)
        self.tool_bar.search_bar.clear()
        self.tool_bar.search_bar.blockSignals(False)

        # Reset logical state
        self.search_text = ''
        self.current_page = 0
        self.foot_bar.pagination.current_page = 0

        match button_id:
            case 0: self.current_db = StudentDirectory
            case 1: self.current_db = ProgramDirectory
            case 2: self.current_db = CollegeDirectory

        self.table_view.table_model.set_database(self.current_db)
        self.table_view.custom_header.blockSignals(True)
        self.table_view.custom_header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.table_view.custom_header.blockSignals(False)
        
        col_name = self.current_db.get_columns()[0]
        self.sort_state = Sorted.By(col_name, ascending = True)

        self.table_view.table.setSortingEnabled(True)
        self.table_view.table.horizontalHeader().setStretchLastSection(True)

        self.fetch_data()

    def fetch_data(self):
        # Asks the active database for exactly what needs to be shown
        where_clause = None
        if self.search_text:
            search_str = self.search_text.lower()
            where_clause = lambda row: any(search_str in str(val).lower() for val in row.values)

        total_matches = self.current_db.get_count(where = where_clause)
        paged_request = Paged.Specific(index = self.current_page + 1, size = self.items_per_page)

        records = self.current_db.get_records(
            where = where_clause, 
            sorted = self.sort_state, 
            paged = paged_request
        )

        self.table_view.table_model.set_data(records)
        self.table_view.table.scrollToTop()
        self.table_view.table.resizeColumnsToContents()

        self.foot_bar.pagination.update_data_stats(total_matches)
        
        visible_count = len(records)
        if total_matches <= self.items_per_page and not self.search_text:
            self.foot_bar.entries_label.setText(f'Showing all {total_matches} entries')
        else:
            self.foot_bar.entries_label.setText(f'Showing {visible_count} of {total_matches} entries')

    def show_custom_message(self, title, message, is_error=False):
        """A beautifully styled, white message box."""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Critical if is_error else QMessageBox.Icon.Information)
        
        # Apply the clean white theme and styled buttons
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
            }
            QPushButton {
                background-color: #8fae44; 
                border: none; 
                border-radius: 4px;
                padding: 6px 20px; 
                color: white; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #7a9638; 
            }
        """)
        msg.exec()

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
        if role == UserRole.ADMIN:
            self.table_card.tool_bar.edit_button.show()
        elif role == UserRole.VIEWER:
            self.table_card.tool_bar.edit_button.hide()