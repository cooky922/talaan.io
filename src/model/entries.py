from enum import Enum
from dataclasses import dataclass 

from src.model.errors import ValidationError, ValidationErrorKind

@dataclass
class FieldInfo:
    internal_name : str
    display_name : str
    underlying_type : type

class EntryKind(Enum):
    STUDENT = 'Student'
    PROGRAM = 'Program'
    COLLEGE = 'College'

    def get_entry_type(self):
        match self:
            case EntryKind.STUDENT:
                return StudentEntry
            case EntryKind.PROGRAM:
                return ProgramEntry
            case EntryKind.COLLEGE:
                return CollegeEntry

class GenderKind(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'

@dataclass
class StudentEntry:
    class FieldKind(Enum):
        ID = FieldInfo(internal_name = 'id', display_name = 'ID Number', underlying_type = int)
        FIRST_NAME = FieldInfo(internal_name = 'first_name', display_name = 'First Name', underlying_type = str)
        LAST_NAME = FieldInfo(internal_name = 'last_name', display_name = 'Last Name', underlying_type = str)
        PROGRAM_CODE = FieldInfo(internal_name = 'program_code', display_name = 'Program Code', underlying_type = str)
        YEAR = FieldInfo(internal_name = 'year', display_name = 'Year Level', underlying_type = int)
        GENDER = FieldInfo(internal_name = 'gender', display_name = 'Gender', underlying_type = GenderKind)

    @staticmethod
    def get_fields() -> dict[StudentEntry.FieldKind, FieldInfo]:
        return {kind.value.internal_name : kind.value for kind in StudentEntry.FieldKind}
    
    @staticmethod
    def validate(field : FieldKind, input : str, program_directory = None):
        if field != StudentEntry.FieldKind.YEAR and len(input) == 0:
            raise ValidationError(EntryKind.STUDENT, field,
                                  ValidationErrorKind.MISSING_FIELD,
                                  field.value.display_name + ' Input is empty')

        match field: 
            case StudentEntry.FieldKind.ID:
                parts = input.split('-')
                if len(parts) != 2:
                    raise ValidationError(EntryKind.STUDENT, 
                                          StudentEntry.FieldKind.ID,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'ID Number must contain exactly one \'-\'')
                for part in parts:
                    if len(part) != 4:
                        raise ValidationError(EntryKind.STUDENT,
                                              StudentEntry.FieldKind.ID,
                                              ValidationErrorKind.INVALID_FORMAT,
                                              'ID Number must be in format 20XX-XXXX')
                    if not part.isdigit():
                        raise ValidationError(EntryKind.STUDENT,
                                              StudentEntry.FieldKind.ID,
                                              ValidationErrorKind.INVALID_FORMAT,
                                              'ID Number must be in digits')
                if not parts[0].startswith('20'):
                    raise ValidationError(EntryKind.STUDENT,
                                          StudentEntry.FieldKind.ID,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'ID Number must start with 20XX')

            case StudentEntry.FieldKind.FIRST_NAME:
                pass

            case StudentEntry.FieldKind.LAST_NAME:
                pass

            case StudentEntry.FieldKind.PROGRAM_CODE:
                if program_directory is not None and not program_directory.has_program(input):
                    raise ValidationError(EntryKind.STUDENT,
                                          StudentEntry.FieldKind.PROGRAM_CODE,
                                          ValidationErrorKind.FOREIGN_KEY_MISSING,
                                          'The given program code does not exist')

            case StudentEntry.FieldKind.YEAR:
                if not isinstance(input, int):
                    raise ValidationError(EntryKind.STUDENT,
                                          StudentEntry.FieldKind.YEAR,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'The input is not a digit')
                if input < 1 or input > 4:
                    raise ValidationError(EntryKind.STUDENT,
                                          StudentEntry.FieldKind.YEAR,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'The year must be from 1 to 4')
                
            case StudentEntry.FieldKind.GENDER:
                if input not in ['Male', 'Female', 'Other']:
                    raise ValidationError(EntryKind.STUDENT,
                                          StudentEntry.FieldKind.GENDER,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'The given gender is not a valid option')
                
    @staticmethod
    def validate_entry(entry : dict[str, str], requires_all = False, program_directory = None):
        for field_kind in StudentEntry.FieldKind:
            if field_kind.value.internal_name not in entry:
                if requires_all:
                    raise ValidationError(EntryKind.STUDENT, None,
                                          ValidationErrorKind.MISSING_FIELD,
                                          'The given input is missing some fields')
                else:
                    continue
            StudentEntry.validate(field_kind, entry[field_kind.value.internal_name], program_directory)

class ProgramEntry:
    class FieldKind(Enum):
        PROGRAM_CODE = FieldInfo(internal_name = 'program_code', display_name = 'Program Code', underlying_type = str)
        PROGRAM_NAME = FieldInfo(internal_name = 'program_name', display_name = 'Program Name', underlying_type = str)
        COLLEGE_CODE = FieldInfo(internal_name = 'college_code', display_name = 'College Code', underlying_type = str)

    @staticmethod
    def get_fields() -> dict[ProgramEntry.FieldKind, FieldInfo]:
        return {kind.value.internal_name : kind.value for kind in ProgramEntry.FieldKind}
    
    @staticmethod
    def validate(field : FieldKind, input : str, college_directory = None):
        if len(input) == 0:
            raise ValidationError(EntryKind.PROGRAM, field,
                                  ValidationErrorKind.MISSING_FIELD,
                                  field.value.display_name + ' Input is empty')
        match field: 
            case ProgramEntry.FieldKind.PROGRAM_CODE:
                pass

            case ProgramEntry.FieldKind.PROGRAM_NAME:
                pass

            case ProgramEntry.FieldKind.COLLEGE_CODE:
                if college_directory is not None and not college_directory.has_college(input):
                    raise ValidationError(EntryKind.COLLEGE,
                                          ProgramEntry.FieldKind.COLLEGE_CODE,
                                          ValidationErrorKind.FOREIGN_KEY_MISSING,
                                          'The given college code does not exist')
                
    @staticmethod
    def validate_entry(entry : dict[str, str], requires_all = False, college_directory = None):
        for field_kind in ProgramEntry.FieldKind:
            if field_kind.value.internal_name not in entry:
                if requires_all:
                    raise ValidationError(EntryKind.PROGRAM, None,
                                          ValidationErrorKind.MISSING_FIELD,
                                          'The given input is missing some fields')
                else:
                    continue
            ProgramEntry.validate(field_kind, entry[field_kind.value.internal_name], college_directory)

class CollegeEntry:
    class FieldKind(Enum):
        COLLEGE_CODE = FieldInfo(internal_name = 'college_code', display_name = 'College Code', underlying_type = str)
        COLLEGE_NAME = FieldInfo(internal_name = 'college_name', display_name = 'College Name', underlying_type = str)

    @staticmethod
    def get_fields() -> dict[CollegeEntry.FieldKind, FieldInfo]:
        return {kind.value.internal_name : kind.value for kind in CollegeEntry.FieldKind}
    
    @staticmethod
    def validate(field : FieldKind, input : str):
        if len(input) == 0:
            raise ValidationError(EntryKind.COLLEGE, field,
                                  ValidationErrorKind.MISSING_FIELD,
                                  field.value.display_name + ' Input is empty')
        match field: 
            case CollegeEntry.FieldKind.COLLEGE_CODE:
                # Must be in one word and all capitals
                if len(input.split()) != 1:
                    raise ValidationError(EntryKind.COLLEGE, 
                                          CollegeEntry.FieldKind.COLLEGE_CODE,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'The college code must contain exactly one word')
                if not input.isupper():
                    raise ValidationError(EntryKind.COLLEGE, 
                                          CollegeEntry.FieldKind.COLLEGE_CODE,
                                          ValidationErrorKind.INVALID_FORMAT,
                                          'The college code must be in uppercase')

            case CollegeEntry.FieldKind.COLLEGE_NAME:
                pass
    
    @staticmethod
    def validate_entry(entry : dict[str, str], requires_all = False):
        for field_kind in CollegeEntry.FieldKind:
            if field_kind.value.internal_name not in entry:
                if requires_all:
                    raise ValidationError(EntryKind.COLLEGE, None,
                                          ValidationErrorKind.MISSING_FIELD,
                                          'The given input is missing some fields')
                else:
                    continue
            CollegeEntry.validate(field_kind, entry[field_kind.value.internal_name])