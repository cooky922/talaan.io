from PyQt6.QtCore import Qt, QAbstractTableModel

class DirectoryTableModel(QAbstractTableModel):
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