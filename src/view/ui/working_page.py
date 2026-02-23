import math
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGridLayout,
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
    QAbstractTableModel, 
    pyqtSignal, 
    QTimer
)
from PyQt6.QtGui import QColor, QCursor, QAction

from src.model.database import (
    StudentDirectory, 
    ProgramDirectory, 
    CollegeDirectory, 
    ConstraintAction, 
    Paged, 
    Sorted
)
from src.model.entries import EntryKind
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
    SearchableComboBox,
    TableHeader,
    ToastNotification,
    MessageBox
)
from src.view.ui.login_page import UserRole

class DirectoryToggleBox(ToggleBox):
    def __init__(self):
        super().__init__(['Students', 'Programs', 'Colleges'], mini = True)

    def set_default(self):
        self.group.buttons()[0].setChecked(True)

class AccountButton(QPushButton):
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

        self.setObjectName('AccountButton')
        self.setStyleSheet(f"""
            {Styles.action_button(
                back_color = Constants.HEADER_BUTTON_COLOR, 
                font_size = 12, 
                text_color = Constants.TEXT_PRIMARY_COLOR, 
                bordered = True,
                id = 'AccountButton')}
            QPushButton#AccountButton::menu-indicator {{ image: none; }}
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

    def create_menu_button(self, text, icon_name, text_color):
        btn = QPushButton()
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        lbl_icon = QLabel()
        lbl_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl_icon.setStyleSheet("background: transparent;")
        lbl_icon.setPixmap(IconLoader.get(icon_name).pixmap(QSize(16, 16)))
        
        # 3. Text Label
        lbl_text = QLabel(text)
        lbl_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl_text.setStyleSheet(f"color: {text_color}; font-size: 11px; font-weight: bold; background: transparent;")
        
        # 4. Add to layout and add a stretch to push them against the left wall
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_text)
        layout.addStretch()
        
        # 5. Clean styling for the button background
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #CCCCCC;
            }}
        """)
        return btn

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
        # self.role_label = InfoLabel('Viewer', fontSize = 12, bold = True)

        self.directory_toggle_box = DirectoryToggleBox()

        self.account_button = AccountButton(role = UserRole.VIEWER)
        self.account_button.logout_requested.connect(self.logout_signal)

        # self.logout_button = QPushButton('Logout')
        # self.logout_button.setIcon(IconLoader.get('logout-light'))
        # self.logout_button.setStyleSheet(Styles.action_button(back_color = Constants.LOGOUT_BUTTON_COLOR, font_size = 12))
        # self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # self.logout_button.clicked.connect(self.logout_signal)

        # Structure
        layout.addSpacing(10)
        layout.addWidget(self.title_label, alignment = Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.directory_toggle_box, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        # layout.addWidget(self.role_label, alignment = Qt.AlignmentFlag.AlignRight)
        # layout.addSpacing(5)
        # layout.addWidget(self.logout_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.account_button, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(10)

class YearStepper(QLineEdit):
    def __init__(self, min_val = 1, max_val = 5, parent = None):
        # Because we inherit from QLineEdit, we initialize it directly!
        super().__init__(str(min_val), parent)
        self.min_val = min_val
        self.max_val = max_val
        
        self.setReadOnly(True)
        self.setTextMargins(0, 0, 0, 0)
        
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                background-color: white;
                color: #333333;
                font-size: 11px;
                padding: 6px 10px;
            }
            QLineEdit:hover { border: 1px solid #8fae44; }
            QLineEdit:focus { border: 1.5px solid #8fae44; background-color: #fcfff5; }
        """)
        
        # 2. THE FLOATING BUTTON CONTAINER
        # By passing 'self' as the parent, this widget lives INSIDE the QLineEdit
        self.btn_container = QWidget(self)
        self.btn_container.setFixedSize(20, 26) 
        
        btn_layout = QVBoxLayout(self.btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0) # Zero gap between + and -
        
        # Transparent buttons so they blend beautifully into the white input field
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: bold;
                color: #888888;
            }
            QPushButton:hover { color: #8fae44; background-color: #f0f4e6; border-radius: 2px;}
            QPushButton:pressed { background-color: #e4ebcc; }
        """
        
        self.btn_plus = QPushButton('+')
        self.btn_plus.setFixedSize(20, 13)
        self.btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_plus.setStyleSheet(btn_style)
        self.btn_plus.clicked.connect(self.increment)
        
        self.btn_minus = QPushButton('-')
        self.btn_minus.setFixedSize(20, 13)
        self.btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minus.setStyleSheet(btn_style)
        self.btn_minus.clicked.connect(self.decrement)
        
        btn_layout.addWidget(self.btn_plus)
        btn_layout.addWidget(self.btn_minus)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        # Move it 2 pixels away from the right edge, perfectly centered vertically
        self.btn_container.move(
            rect.width() - self.btn_container.width() - 2, 
            (rect.height() - self.btn_container.height()) // 2
        )

    def increment(self):
        current = int(self.text() or self.min_val)
        if current < self.max_val:
            self.setText(str(current + 1))

    def decrement(self):
        current = int(self.text() or self.min_val)
        if current > self.min_val:
            self.setText(str(current - 1))
            
    def setText(self, text):
        if text and str(text).isdigit():
            val = max(self.min_val, min(self.max_val, int(text)))
            super().setText(str(val))

class EntryDialog(QDialog):
    def __init__(self, current_db, record=None, parent=None):
        super().__init__(parent)
        self.current_db = current_db
        self.record = record
        self.is_edit_mode = record is not None
        self.is_deleted = False
        
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        match self.current_db.get_entry_kind():
            case EntryKind.STUDENT:
                self.setFixedWidth(350)
            case EntryKind.PROGRAM:
                self.setFixedWidth(400)
            case EntryKind.COLLEGE:
                self.setFixedWidth(400)
            
        self.setObjectName('EntryDialog')
        self.setStyleSheet("""
            QDialog#EntryDialog { background-color: #ffffff; }
            QLabel { color: #333333; }
        """)
        
        title_text = 'Edit Record' if self.is_edit_mode else 'Add Record'
        title_text = title_text.replace('Record', self.current_db.get_entry_kind().value)
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
        
        columns = self.current_db.get_columns()
        primary_key = self.current_db._db.primary_key
        
        row_idx = 0
        col_idx = 0
        
        for col_name in columns:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(5)
            
            label_text = self.current_db.get_entry_kind().get_entry_type().get_fields()[col_name].display_name
            
            lbl = QLabel(label_text.upper())
            lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #555555;")
            field_layout.addWidget(lbl)
            
            # Pass the label_text to create placeholders!
            input_widget = self.create_input_widget(col_name, label_text)
            
            # Only lock the id if we are editing a student entry
            if self.is_edit_mode and col_name == primary_key and self.current_db.get_entry_kind() == EntryKind.STUDENT:
                if isinstance(input_widget, QComboBox):
                    input_widget.setEnabled(False)
                else:
                    input_widget.setReadOnly(True)
                
                # Apply the dashed border, gray background, and Forbidden Cursor
                disabled_css = """
                    background-color: #f7f7f7 !important;
                    color: #aaaaaa !important;
                    border: 1px solid #cccccc !important;
                """

                override_css = f"""
                    QLineEdit {{ {disabled_css} }}
                    QLineEdit:focus {{ {disabled_css} }}
                    QComboBox {{ {disabled_css} }}
                    QComboBox:focus {{ {disabled_css} }}
                """

                input_widget.setStyleSheet(input_widget.styleSheet() + override_css)
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
        footer_layout.setSpacing(5)

        self.delete_button = None

        if self.is_edit_mode:
            self.delete_button = QPushButton('Delete')
            self.delete_button.setIcon(IconLoader.get('delete-light'))
            self.delete_button.setStyleSheet(Styles.action_button(back_color = Constants.DANGER_COLOR, font_size = 11))
            self.delete_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.delete_button.clicked.connect(self.request_delete)
            footer_layout.addWidget(self.delete_button)

        footer_layout.addStretch()

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setStyleSheet(Styles.action_button(back_color = Constants.BUTTON_SECONDARY_COLOR, text_color = '#333333', font_size = 11, bordered = True))
        self.cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_button.clicked.connect(self.reject)

        self.action_button = QPushButton('Save' if self.is_edit_mode else 'Add')
        self.action_button.setStyleSheet(Styles.action_button(back_color = Constants.ACTIVE_BUTTON_COLOR, font_size = 11))
        self.action_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.action_button.clicked.connect(self.request_proceed)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.action_button)
        main_layout.addLayout(footer_layout)

        self.adjustSize()
        self.setFixedHeight(self.height())

    def create_input_widget(self, col_name, label_text):
        base_style = """
            border: 1px solid #CCCCCC;
            border-radius: 10px;
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
            QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {{
                background-color: #f0f4e6;
                color: #333333;
            }}
            QLineEdit {{
                background: transparent; border: none; padding: 0px; color: #333333; font-size: 11px;
            }}
            QLineEdit::placeholder {{ color: #bbbbbb; }}

            {Styles.combobox_dropdown()}
        """

        placeholder = f'Enter {label_text.lower()}'
        select_placeholder = f'Select {label_text.lower()}'

        if col_name == 'gender': 
            cb = SearchableComboBox(['Male', 'Female', 'Other'], select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        elif col_name == 'year': 
            return YearStepper(min_val = 1, max_val = 4)
            
        elif col_name == 'program_code' and self.current_db.get_entry_kind() == EntryKind.STUDENT:
            cb = SearchableComboBox(sorted(ProgramDirectory.get_keys()), select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        elif col_name == 'college_code' and self.current_db.get_entry_kind() == EntryKind.PROGRAM:
            cb = SearchableComboBox(sorted(CollegeDirectory.get_keys()), select_placeholder)
            cb.setStyleSheet(combo_style)
            return cb
            
        else:
            le = QLineEdit()
            le.setPlaceholderText(placeholder)
            le_style = f"QLineEdit {{ {base_style} padding: 6px 10px; }} QLineEdit{interactive_states} QLineEdit::placeholder {{ color: #bbbbbb; }}"
            le.setStyleSheet(le_style)
            return le
        
    def confirm_rename_changes(self, count, old_key, new_key):
        message = f'Are you sure you want to rename this {old_key} to {new_key}?\n\nThis action cannot be undone.'
        if self.current_db.get_entry_kind() == EntryKind.PROGRAM:
            message += f'\nThis also means renaming all {count} student entries\' program code.'
        elif self.current_db.get_entry_kind() == EntryKind.COLLEGE:
            message += f'\nThis also means renaming all {count} program entries\' college code.'

        msg = MessageBox(self, title = 'Confirm Rename', message = message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        return msg.exec()
        
    def request_proceed(self):
        if not self.is_edit_mode:
            self.accept()
            return
        new_data = self.get_data()
        primary_key = self.current_db.get_primary_key()
        old_key_value = self.record[primary_key]
        new_key_value = new_data[primary_key]
        count = 0
        if old_key_value != new_key_value:
            if self.current_db.get_entry_kind() == EntryKind.PROGRAM:
                count = StudentDirectory.get_count(where = f'program_code == \'{old_key_value}\'')
            elif self.current_db.get_entry_kind() == EntryKind.COLLEGE:
                count = ProgramDirectory.get_count(where = f'college_code == \'{old_key_value}\'')
        if count > 0:
            result = self.confirm_rename_changes(count, old_key_value, new_key_value)
            if result == int(QMessageBox.StandardButton.Yes) or result == QMessageBox.StandardButton.Yes:
                self.accept()
            else:
                self.reject()
        else:
            self.accept()
            return
        
    def request_delete(self):
        message = 'Are you sure you want to delete this record?\n\nThis action cannot be undone.'
        input_data = self.get_data()
        if self.current_db.get_entry_kind() == EntryKind.PROGRAM:
            old_program_code = input_data['program_code']
            count = StudentDirectory.get_count(where = f'program_code == \'{old_program_code}\'')
            if count > 0:
                message += f'\nThis also means deleting {count} student entries with program code {old_program_code}.'
        elif self.current_db.get_entry_kind() == EntryKind.COLLEGE:
            old_college_code = input_data['college_code']
            program_list = ProgramDirectory.get_records(where = f'college_code == \'{old_college_code}\'')
            program_count = len(program_list)
            if program_count > 0:
                message += f'\nThis also means deleting {program_count} program entries with college code {old_college_code}.'
                count = 0
                for program_entry in program_list:
                    student_count = StudentDirectory.get_count(where = f'program_code == \'{program_entry['program_code']}\'')
                    count = count + student_count
                if count > 0:
                    message += f'\nThis also means deleting {count} student entries associated with the college code.'
        msg = MessageBox(self, title = 'Confirm Delete', message = message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        result = msg.exec()
        if result == int(QMessageBox.StandardButton.Yes) or result == QMessageBox.StandardButton.Yes:
            self.is_deleted = True
            self.accept()

    def populate_data(self):
        if not self.is_edit_mode: return
        for col_name, widget in self.inputs.items():
            val = str(self.record.get(col_name, ''))
            if isinstance(widget, QComboBox): 
                widget.setCurrentText(val)
            elif isinstance(widget, YearStepper):
                widget.setText(val)
            elif isinstance(widget, QLineEdit): 
                widget.setText(val)

    def get_data(self) -> dict:
        data = {}
        for col_name, widget in self.inputs.items():
            val = None
            if isinstance(widget, QComboBox):
                val = widget.currentText()
            elif isinstance(widget, YearStepper) or isinstance(widget, QLineEdit):
                val = widget.text()
            else:
                val = ''
            if col_name == 'year':
                data[col_name] = int(val)
            else:
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
            return self._db.get_entry_kind().get_entry_type().get_fields()[self._headers[section]].display_name.upper()
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

        self.search_filter = QComboBox()
        self.search_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_filter.setFixedWidth(140)
        self.search_filter.setIconSize(QSize(16, 16))
        self.search_filter.setItemDelegate(NoIconDelegate(self.search_filter))
        self.search_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 15px;
                background-color: white;
                color: #555555;
                font-size: 11px;
                padding: 8px 10px;
            }
            QComboBox:hover { border: 1px solid #8fae44; }
            QComboBox::drop-down { 
                subcontrol-origin: padding; 
                subcontrol-position: top right; 
                width: 20px; 
                border-left: none; 
            }
            QComboBox::down-arrow { image: none; } /* Hide default arrow */
            QComboBox QAbstractItemView {
                background-color: white; color: #333333; border: 1px solid #CCCCCC;
                selection-background-color: #f0f4e6; selection-color: #333333; outline: none;
                border-radius: 15px;
            }
            QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {
                background-color: #f0f4e6;
                color: #333333;
            }
        """)

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


class PaginationControl(QWidget):
    # Custom signal that alerts the main page to fetch new data chunks
    page_changed = pyqtSignal(int)

    def __init__(self, items_per_page = 100):
        super().__init__()
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_rows = 0

        self.setStyleSheet(Styles.pagination_control())
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
        super().__init__('TableCard', size = QSize(700, 350))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
        self.tool_bar.search_filter.currentIndexChanged.connect(self.on_search_triggered)

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
        record = self.table_view.table_model._data[index.row()]
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

        self.table_view.table_model.set_data(records)
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

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 0, 40, 40)
        content_layout.addWidget(self.table_card)

        # Structure
        layout.addWidget(self.header)
        layout.addSpacing(10)
        layout.addLayout(content_layout)

    def set_role(self, role : UserRole):
        self.role = role
        self.header.account_button.setRole(role)
        if role == UserRole.ADMIN:
            self.table_card.tool_bar.edit_button.show()
        elif role == UserRole.VIEWER:
            self.table_card.tool_bar.edit_button.hide()

    def set_default(self):
        self.header.directory_toggle_box.set_default()
        self.table_card.tool_bar.reset_mode()
        self.table_card.switch_table(0)