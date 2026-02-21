from enum import Enum

class ArgumentError(Exception):
    def __init__(self, message):
        super().__init__(message)

class DatabaseErrorKind(Enum):
    INVALID_QUERY = 'Invalid query'
    UNDEFINED_PRIMARY_KEY = 'No primary key defined for this database'
    NO_KEY = 'An entry with key does not exist'
    DUPLICATE_KEY = 'The key already exists'
    CHANGE_KEY = 'The key cannot be changed'
    HEADER_NAME_NOT_FOUND = 'Header name not found'

class DatabaseError(Exception):
    def __init__(self, error_kind, message = None):
        self.error_kind = error_kind
        self.message = message if message is not None else error_kind.value
        super().__init__(self.message)

class ValidationErrorKind(Enum):
    DUPLICATE_KEY = 'Duplicate Key'
    FOREIGN_KEY_MISSING = 'Foreign Key Missing'
    INVALID_FORMAT = 'Invalid Format'
    MISSING_FIELD = 'Missing Field'

class ValidationError(Exception):
    def __init__(self, entry_kind, field_kind, error_kind, message):
        super().__init__(message)
        self.entry_kind = entry_kind
        self.field_kind = field_kind
        self.error_kind = error_kind
        self.message = message