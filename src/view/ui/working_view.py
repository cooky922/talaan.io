import math
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableView,
    QWidget, 
    QWidgetAction,
    QVBoxLayout
)
from PyQt6.QtCore import (
    Qt,
    QSize,
    pyqtSignal, 
    QTimer
)
from PyQt6.QtGui import QCursor

from src.model.role import UserRole
from src.model.entries import EntryKind
from src.model.database import (
    StudentDirectory, 
    ProgramDirectory, 
    CollegeDirectory, 
    ConstraintAction, 
    Paged, 
    Sorted
)
from src.model.table_model import DirectoryTableModel
from src.utils.constants import Constants
from src.utils.styles import Styles
from src.utils.icon_loader import IconLoader

from src.view.components import (
    TitleLabel, 
    InfoLabel, 
    ToggleBox, 
    Card,
    NoIconDelegate,
    RowHoverDelegate,
    TableHeader,
    ToastNotification,
    MessageBox
)
from src.view.ui.entry_dialog import EntryDialog

class DirectoryToggleArea(ToggleBox):
    def __init__(self):
        super().__init__(['Students', 'Programs', 'Colleges'], mini = True)

    def set_default(self):
        self.group.buttons()[0].setChecked(True)

class AccountArea(QPushButton):
    logout_requested = pyqtSignal()
    about_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, role : UserRole, parent = None):
        super().__init__('', parent)
        self.setMinimumWidth(100)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.role_label = QLabel(role.value)
        self.role_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.role_label.setStyleSheet(Styles.info_label(bold = True, color = Constants.TEXT_PRIMARY_COLOR))
        self.role_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.icon_label = QLabel()
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.icon_label.setStyleSheet('background: transparent;')

        pixmap = IconLoader.get('account-dark').pixmap(QSize(24, 24))
        self.icon_label.setPixmap(pixmap)

        layout.addWidget(self.role_label)
        layout.addWidget(self.icon_label)

        # Account menu
        self.account_menu = QMenu(self)
        self.account_menu.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.account_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        base_css = 'QPushButton { text-align: left; }'

        ## Settings button
        self.settings_action = QWidgetAction(self)
        self.settings_button = QPushButton('  Settings')
        self.settings_button.setIcon(IconLoader.get('settings-dark'))
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setStyleSheet(base_css + Styles.action_button(
            back_color = 'white',
            text_color = Constants.TEXT_PRIMARY_COLOR,
            font_size = 11,
        ))
        self.settings_button.clicked.connect(self.trigger_settings)

        self.settings_action.setDefaultWidget(self.settings_button)
        self.account_menu.addAction(self.settings_action)

        ## About button
        self.about_action = QWidgetAction(self)
        self.about_button = QPushButton('  About')
        self.about_button.setIcon(IconLoader.get('info-dark'))
        self.about_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.about_button.setStyleSheet(base_css + Styles.action_button(
            back_color = 'white',
            text_color = Constants.TEXT_PRIMARY_COLOR,
            font_size = 11,
        ))

        self.about_button.clicked.connect(self.trigger_about)

        self.about_action.setDefaultWidget(self.about_button)
        self.account_menu.addAction(self.about_action)

        self.account_menu.addSeparator()

        ## Logout button
        self.logout_action = QWidgetAction(self)
        self.logout_button = QPushButton('  Logout')
        self.logout_button.setIcon(IconLoader.get('logout-light'))
        self.logout_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logout_button.setStyleSheet(base_css + Styles.action_button(
            back_color = Constants.DANGER_COLOR,
            font_size = 11,
        ))
        self.logout_button.clicked.connect(self.trigger_logout)

        self.logout_action.setDefaultWidget(self.logout_button)
        self.account_menu.addAction(self.logout_action)

        self.setMenu(self.account_menu)

        self.setObjectName('AccountArea')
        self.setStyleSheet(f"""
            {Styles.action_button(
                back_color = Constants.HEADER_BUTTON_COLOR, 
                font_size = 12, 
                text_color = Constants.TEXT_PRIMARY_COLOR, 
                bordered = True,
                id = 'AccountArea')}
            QPushButton#AccountArea::menu-indicator {{ image: none; }}
        """)

        self.account_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                padding: 4px 10px; 
            }
            QMenu::item {
                padding: 8px 10px; 
                color: #333333;
                font-size: 11px;
                font-weight: bold;
            }
                                        
            QMenu::separator {
                height: 2px;
                border-radius: 10px;
                background-color: #CCCCCC; /* Light gray line */
                margin: 8px 4px;           /* Gives it some breathing room from the sides */
            }
        """)

    def trigger_logout(self):
        self.account_menu.close()
        self.logout_requested.emit()

    def trigger_settings(self):
        self.account_menu.close()
        self.settings_requested.emit()

    def trigger_about(self):
        self.account_menu.close()
        self.about_requested.emit()

    def setRole(self, role : UserRole):
        self.role_label.setText(role.value)

class PaginationArea(QWidget):
    # Custom signal that alerts the main page to fetch new data chunks
    page_changed = pyqtSignal(int)

    def __init__(self, items_per_page = 100):
        super().__init__()
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_rows = 0

        self.setStyleSheet(Styles.pagination_area())
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_entries = InfoLabel('Page 1 out of 1', color = Constants.TEXT_SECONDARY_COLOR)

        self.page_btn_layout = QHBoxLayout()
        self.page_btn_layout.setSpacing(2)

        self.main_layout.addWidget(self.lbl_entries)
        self.main_layout.addSpacing(10)
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

        self.lbl_entries.setText(f'Page {self.current_page + 1} out of {total_pages}')

        for i in reversed(range(self.page_btn_layout.count())):
            item = self.page_btn_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        btn_prev = QPushButton()
        btn_prev.setIcon(IconLoader.get('arrow-backward-gray'))
        btn_prev.setObjectName('NavArrow')
        btn_prev.setFixedSize(25, 25)
        btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_next.setEnabled(self.current_page < total_pages - 1)
        btn_next.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        self.page_btn_layout.addWidget(btn_next)

    def _add_page_btn(self, page_num):
        btn = QPushButton(str(page_num + 1))
        btn.setObjectName('PageButton')
        btn.setFixedSize(25, 25)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setProperty('active', page_num == self.current_page)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        btn.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_btn_layout.addWidget(btn)

    def _add_dots(self):
        lbl = InfoLabel('. . .', color = Constants.TEXT_SECONDARY_COLOR)
        lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.page_btn_layout.addWidget(lbl)

class MainHeader(QWidget):
    def __init__(self, signal):
        super().__init__()
        self.logout_signal = signal

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('MainHeader')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(Styles.header())

        # Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Elements
        self.title_label = TitleLabel('talaan.io', fontSize = 24)

        self.directory_toggle_area = DirectoryToggleArea()
        self.account_area = AccountArea(role = UserRole.VIEWER)
        self.account_area.logout_requested.connect(self.logout_signal)

        # Structure
        layout.addSpacing(10)
        layout.addWidget(self.title_label, alignment = Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.directory_toggle_area, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.account_area, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(10)

class DirectoryTable(QWidget):
    def __init__(self):
        super().__init__()
        
        self.resize(650, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        self.model = DirectoryTableModel(StudentDirectory)
        self.table = QTableView()

        self.hover_delegate = RowHoverDelegate(self.table)
        self.custom_header = TableHeader(Qt.Orientation.Horizontal, self.table)
        self.table.setHorizontalHeader(self.custom_header)

        self.table.setItemDelegate(self.hover_delegate)
        self.table.setStyleSheet(Styles.table())

        self.table.setModel(self.model)
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


class DirectoryToolBar(QWidget):
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

        self.search_filter = QComboBox()
        self.search_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_filter.setFixedWidth(140)
        self.search_filter.setIconSize(QSize(16, 16))
        self.search_filter.setItemDelegate(NoIconDelegate(self.search_filter))
        self.search_filter.setStyleSheet(Styles.search_filter())

        self.add_button = QPushButton(' Add Student')
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
        layout.addWidget(self.search_filter)
        layout.addStretch()
        layout.addWidget(self.add_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.edit_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(15)

    def toggle_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.setText(' Done')
            self.edit_button.setIcon(IconLoader.get('done-dark'))
            self.edit_button.setStyleSheet(Styles.action_button(back_color = Constants.BUTTON_SECONDARY_COLOR, font_size = 12, text_color = '#333333', bordered = True))
            self.add_button.show()
        else:
            self.edit_button.setText(' Edit')
            self.edit_button.setIcon(IconLoader.get('edit-light'))
            self.edit_button.setStyleSheet(Styles.action_button(back_color = Constants.ACTIVE_BUTTON_COLOR, font_size = 12))
            self.add_button.hide()
        self.edit_mode_toggled.emit(self.is_edit_mode)

    def reset_mode(self):
        if self.is_edit_mode:
            self.toggle_mode()

class DirectoryFootBar(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.setLayout(layout)

        # Component
        self.entries_label = InfoLabel('Results', color = Constants.TEXT_SECONDARY_COLOR)
        
        # Initialized independently without proxy/table references
        self.pagination = PaginationArea(items_per_page = 100)

        # Structure
        layout.addSpacing(15)
        layout.addWidget(self.entries_label, alignment = Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.pagination)
        layout.addSpacing(15)

class MainBody(Card):
    def __init__(self):
        super().__init__('MainBody', size = QSize(700, 350))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # State Tracking
        self.current_db = StudentDirectory
        self.search_text = ""
        self.sort_state = None
        self.current_page = 0
        self.items_per_page = 100

        # Components
        self.table_view = DirectoryTable()
        self.tool_bar = DirectoryToolBar()
        self.foot_bar = DirectoryFootBar()

        # Wire Up the Debounce Search Timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(10)
        self.search_timer.timeout.connect(self.on_search_triggered)
        self.tool_bar.search_bar.textChanged.connect(self.search_timer.start)
        self.tool_bar.search_filter.currentIndexChanged.connect(self.on_search_triggered)

        # Wire Up Pagination & Sorting Signals
        self.tool_bar.add_button.clicked.connect(self.open_add_dialog)
        self.table_view.custom_header.sortIndicatorChanged.connect(self.on_sort_changed)
        self.table_view.table.clicked.connect(self.on_row_clicked)
        self.foot_bar.pagination.page_changed.connect(self.on_page_changed)

        # Layout
        layout.addSpacing(10)
        layout.addWidget(self.tool_bar)
        layout.addWidget(self.table_view)
        layout.addWidget(self.foot_bar)
        layout.addSpacing(10)

        # Booting
        self.table_view.custom_header.blockSignals(True)
        self.table_view.custom_header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.table_view.custom_header.blockSignals(False)

        self.tool_bar.search_filter.addItem(IconLoader.get('filter-dark'), 'All Fields', userData = 'ALL')
        fields_info = self.current_db.get_entry_kind().get_entry_type().get_fields()
        for col in self.current_db.get_columns():
            self.tool_bar.search_filter.addItem(IconLoader.get('filter-dark'), fields_info[col].display_name, userData = col)

        col_name = self.current_db.get_columns()[0]
        self.sort_state = Sorted.By(col_name, ascending = True)
        self.fetch_data()

        # Toast setup
        self.toast = ToastNotification(self)

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
        record = self.table_view.model._data[index.row()]
        primary_key = self.current_db._db.primary_key
        key_value = record[primary_key]

        dialog = EntryDialog(self.current_db, record = record, parent = self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.is_deleted:
                try:
                    if self.current_db.get_entry_kind() == EntryKind.STUDENT:
                        self.current_db.delete_record(key = key_value)
                    else:
                        self.current_db.delete_record(key = key_value, action = ConstraintAction.Cascade)
                    self.fetch_data()
                    self.toast.show_message('row deleted')
                except Exception as e:
                    self.show_custom_message('Error', f'Failed to delete record\n{str(e)}', is_error = True)
            else:
                new_data = dialog.get_data()
                try:
                    if self.current_db.get_entry_kind() ==  EntryKind.STUDENT:
                        self.current_db.update_record(new_data, key = key_value)
                    else:
                        self.current_db.update_record(new_data, key = key_value, action = ConstraintAction.Cascade)
                    self.fetch_data()
                    self.toast.show_message('row updated')
                except Exception as e:
                    self.show_custom_message('Error', f'Failed to update record\n{str(e)}', is_error = True)

    def open_add_dialog(self):
        dialog = EntryDialog(self.current_db, record = None, parent = self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                self.current_db.add_record(new_data)
                self.fetch_data()
                self.toast.show_message('record added')
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

        self.tool_bar.search_filter.blockSignals(True)
        self.tool_bar.search_filter.clear()
        self.tool_bar.search_filter.addItem(IconLoader.get('filter-dark'), 'All Fields', userData = 'ALL')
        fields_info = self.current_db.get_entry_kind().get_entry_type().get_fields()
        for col in self.current_db.get_columns():
            self.tool_bar.search_filter.addItem(IconLoader.get('filter-dark'), fields_info[col].display_name, userData  = col)
        self.tool_bar.search_filter.blockSignals(False)

        self.tool_bar.add_button.setText(' Add ' + self.current_db.get_entry_kind().value)

        self.table_view.model.set_database(self.current_db)
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
            target_col = self.tool_bar.search_filter.currentData()
            if target_col.upper() == 'ALL' or not target_col:
                where_clause = lambda row: any(search_str in str(val).lower() for val in row.values)
            else:
                where_clause = lambda row: search_str in str(row.get(target_col, '')).lower()

        total_matches = self.current_db.get_count(where = where_clause)
        paged_request = Paged.Specific(index = self.current_page + 1, size = self.items_per_page)

        records = self.current_db.get_records(
            where = where_clause, 
            sorted = self.sort_state, 
            paged = paged_request
        )

        self.table_view.model.set_data(records)
        self.table_view.table.scrollToTop()
        self.table_view.table.resizeColumnsToContents()

        self.foot_bar.pagination.update_data_stats(total_matches)
        
        visible_count = len(records)
        if total_matches <= self.items_per_page and not self.search_text:
            self.foot_bar.entries_label.setText(f'Showing all {total_matches} entries')
        else:
            self.foot_bar.entries_label.setText(f'Showing {visible_count} of {total_matches} entries')

    def show_custom_message(self, title, message, is_error = False):
        msg = MessageBox(self, title, message)
        msg.setIcon(QMessageBox.Icon.Critical if is_error else QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        msg.exec()

class WorkingView(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('WorkingView')
        self.setStyleSheet(Styles.page('WorkingView'))

        # Role
        self.role = None

        # Layout 
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Elements
        self.header = MainHeader(self.logout_signal)
        self.body = MainBody()
        self.header.directory_toggle_area.group.idClicked.connect(self.body.switch_table)

        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(40, 0, 40, 40)
        body_layout.addWidget(self.body)

        # Structure
        layout.addWidget(self.header)
        layout.addSpacing(10)
        layout.addLayout(body_layout)

    def set_role(self, role : UserRole):
        self.role = role
        self.header.account_area.setRole(role)
        if role == UserRole.ADMIN:
            self.body.tool_bar.edit_button.show()
        elif role == UserRole.VIEWER:
            self.body.tool_bar.edit_button.hide()

    def set_default(self):
        self.header.directory_toggle_area.set_default()
        self.body.tool_bar.reset_mode()
        self.body.switch_table(0)