from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from src.model.entries import EntryKind
from src.model.database import (
    StudentDirectory, 
    ProgramDirectory, 
    CollegeDirectory
)
from src.utils.constants import Constants
from src.utils.styles import Styles
from src.utils.icon_loader import IconLoader

from src.view.components import (
    YearStepper,
    SearchableComboBox,
    MessageBox
)

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