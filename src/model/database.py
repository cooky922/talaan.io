from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union, Callable, Optional, Iterator, List
import pandas as pd

class ConstraintAction(Enum):
    Cascade = "Cascade"    # automatically updates/deletes related records when the referenced record is updated/deleted
    SetNull = "SetNull"    # sets the value to null (or a default) when the related record is deleted/updated
    Restrict = "Restrict"  # prevents the change and raises an error    

@dataclass
class Sorted:
    column: str
    ascending: bool = True
    
    @staticmethod
    def By(column: str, ascending: bool = True):
        return Sorted(column, ascending)

@dataclass
class Paged:
    size: int
    index: Optional[int] = None

    @staticmethod
    def Specific(index: int, size: int):
        """Get a specific page (e.g., Page 2 of size 50)"""
        return Paged(size=size, index=index)

    @staticmethod
    def Stream(size: int):
        """Get a generator that yields chunks of this size"""
        return Paged(size=size, index=None)

# Generic CSV Database with CRUD operations and query capabilities
class GenericDatabase:
    def __init__(self, file_path: Path, primary_key: str = None):
        self.file_path = file_path
        self.modified = False

        if not file_path.exists():
            self.df = pd.DataFrame()
        else:
            try:
                self.df = pd.read_csv(str(file_path))
            except pd.errors.EmptyDataError:
                self.df = pd.DataFrame()

        if primary_key:
            self.primary_key = primary_key
        else:
            self.primary_key = self.df.columns[0] if not self.df.empty else None

    def get_count(self,
                  where: Union[str, Callable] = None) -> int:
        if where:
            temp_df = self.df.copy()
            if isinstance(where, str):
                try:
                    temp_df = temp_df.query(where)
                except Exception as e:
                    raise ValueError(f"Invalid query: {where}. Error: {e}")
            elif callable(where):
                temp_df = temp_df[temp_df.apply(where, axis=1)]
            return len(temp_df)
        else:
            return len(self.df)
        
    def get_columns(self) -> List[str]:
        return self.df.columns.tolist()
    
    def get_keys(self) -> List[str]:
        return self.df[self.primary_key].astype(str).tolist() if self.primary_key else []
    
    def has_key(self, key: str) -> bool:
        if not self.primary_key:
            raise ValueError("No primary key defined for this database.")
        return key in self.df[self.primary_key].astype(str).values
    
    # filter -> sort -> paginate 
    def get_records_as_dataframe(self, 
                                where: Union[str, Callable] = None,
                                sort: Optional[Sorted] = None,
                                page: Optional[Paged] = None) -> pd.DataFrame:
        temp_df = self.df.copy() # Work on a copy to avoid sorting the actual DB
        # 1. Filter
        if where:
            if isinstance(where, str):
                try:
                    temp_df = temp_df.query(where)
                except Exception as e:
                    raise ValueError(f"Invalid query: {where}. Error: {e}")
            elif callable(where):
                temp_df = temp_df[temp_df.apply(where, axis=1)]
        # 2. Sort
        if sort:
            if sort.column in temp_df.columns:
                temp_df = temp_df.sort_values(by=sort.column, ascending=sort.ascending)
            else:
                raise ValueError(f"Sort column '{sort.column}' not found.")
        # 3. Paginate
        if page and page.index is not None:
            start = (page.index - 1) * page.size
            end = start + page.size
            temp_df = temp_df.iloc[start:end]
        return temp_df

    # filter -> sort -> paginate
    def get_records(self, 
                    where: Union[str, Callable] = None, 
                    sorted: Optional[Sorted] = None, 
                    paged: Optional[Paged] = None) -> Union[List[dict], Iterator[List[dict]]]:
        
        temp_df = self.df.copy() # Work on a copy to avoid sorting the actual DB

        # 1. Filter
        if where:
            if isinstance(where, str):
                try:
                    temp_df = temp_df.query(where)
                except Exception as e:
                    raise ValueError(f"Invalid query: {where}. Error: {e}")
            elif callable(where):
                temp_df = temp_df[temp_df.apply(where, axis=1)]

        # 2. Sort
        if sorted:
            if sorted.column in temp_df.columns:
                temp_df = temp_df.sort_values(by=sorted.column, ascending=sorted.ascending)
            else:
                raise ValueError(f"Sort column '{sorted.column}' not found.")

        # 3. Chunk/Paginate
        if paged:
            if paged.index is not None:
                # Specific Page
                start = (paged.index - 1) * paged.size
                end = start + paged.size
                return temp_df.iloc[start:end].to_dict('records')
            else:
                # Stream (Generator)
                def chunk_generator():
                    total = len(temp_df)
                    for start in range(0, total, paged.size):
                        yield temp_df.iloc[start : start + paged.size].to_dict('records')
                return chunk_generator()

        return temp_df.to_dict('records')
    
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        if index is not None and key is not None:
            raise ValueError("Provide either 'index' or 'key', not both.")
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise IndexError("Record index out of range")
            return self.df.iloc[index].to_dict()
        elif key is not None:
            if not self.primary_key:
                raise ValueError("No primary key defined for this database.")
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise KeyError(f"Record with key '{key}' not found.")
            return filtered_df.iloc[0].to_dict()
        else:
            raise TypeError("Index must be an integer or string.")

    def add_record(self, record: dict):
        if self.df.empty:
            self.df = pd.DataFrame([record])
            if not self.primary_key: self.primary_key = list(record.keys())[0]
            self.modified = True
            return
        if self.primary_key:
            pk_val = record.get(self.primary_key)
            if pk_val and str(pk_val) in self.df[self.primary_key].astype(str).values:
                raise ValueError(f"Duplicate Key: {pk_val} already exists.")

        self.df = pd.concat([self.df, pd.DataFrame([record])], ignore_index=True)
        self.modified = True
    
    def update_records(self, where: Union[str, Callable], updates: dict):
        """Update multiple rows based on a condition."""
        if self.df.empty: return

        if isinstance(where, str):
            mask = self.df.eval(where)
        elif callable(where):
            mask = self.df.apply(where, axis=1)
        else:
            return

        for key, value in updates.items():
            if key in self.df.columns:
                self.df.loc[mask, key] = value
        self.modified = True

    def update_record(self, updates: dict, *, index : int = None, key : str = None):
        """Update a single row by its specific index (0 to N)."""
        if index is not None and key is not None:
            raise ValueError("Provide either 'index' or 'key', not both.")
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise IndexError("Record index out of range")
        elif key is not None:
            if not self.primary_key:
                raise ValueError("No primary key defined for this database.")
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise KeyError(f"Record with key '{key}' not found.")
            index = filtered_df.index[0]
        if self.primary_key and self.primary_key in updates:
            new_pk = str(updates[self.primary_key])
            current_pk = str(self.df.at[index, self.primary_key])            
            if new_pk != current_pk:
                if new_pk in self.df[self.primary_key].astype(str).values:
                    raise ValueError(f"Cannot update. Key {new_pk} already exists.")
        idx = index if index is not None else key
        for updated_key, updated_value in updates.items():
            if updated_key in self.df.columns:
                self.df.at[idx, updated_key] = updated_value
        self.modified = True

    def delete_records(self, where: Union[str, Callable]):
        """Delete multiple rows based on a condition."""
        if self.df.empty: return

        if isinstance(where, str):
            mask = self.df.eval(where)
            # Invert mask to keep rows that DO NOT match
            self.df = self.df[~mask]
        elif callable(where):
            mask = self.df.apply(where, axis=1)
            self.df = self.df[~mask]

        self.df.reset_index(drop=True, inplace=True)
        self.modified = True

    def delete_record(self, *, index: int = None, key: str = None):
        """Delete a single row by its specific index or a key value."""
        if index is not None and key is not None:
            raise ValueError("Provide either 'index' or 'key', not both.")
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise IndexError("Record index out of range")
            self.df = self.df.drop(index).reset_index(drop=True)
        elif key is not None:
            if not self.primary_key:
                raise ValueError("No primary key defined for this database.")
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise KeyError(f"Record with key '{key}' not found.")
            self.df = self.df[self.df[self.primary_key].astype(str) != key].reset_index(drop=True)
        self.modified = True

    def save(self):
        if self.modified:
            self.df.to_csv(self.file_path, index=False)
            self.modified = False

# Handles student-specific records and validates inputs
@dataclass
class StudentRecord:
    class Gender(Enum):
        Male = "Male"
        Female = "Female"
        Other = "Other"

    # Student attributes
    id : int
    first_name : int
    last_name : int
    program_code : str
    year : int
    gender : Gender

    @staticmethod
    def _is_valid_id(id_str: str) -> bool:
        parts = id_str.split('-')
        if len(parts) != 2:
            return False
        return all(part.isdigit() and len(part) == 4 for part in parts)
    
    @staticmethod
    def _is_valid_year(year_str : str) -> bool:
        return year_str.isdigit() and 1 <= int(year_str) <= 5
    
    @staticmethod
    def _is_valid_gender(gender_str : str) -> bool:
        return gender_str in ['Male', 'Female', 'Other']
    
    @staticmethod
    def column_display_name(column : str) -> str:
        column_name_map = {
            'id': 'ID Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'program_code': 'Program Code',
            'year': 'Year Level',
            'gender': 'Gender'
        }
        return column_name_map.get(column, '')

    @staticmethod
    def is_valid(record: dict[str, str], check_all = True) -> bool:
        # Implement validation logic (e.g., check required fields, data types, etc.)
        required_fields = ['id', 'first_name', 'last_name', 'program_code', 'year', 'gender']
        for field in required_fields:
            if field not in record:
                if check_all:
                    return False
                else:
                    continue
            match field:
                case 'id':
                    if not StudentRecord._is_valid_id(record[field]):
                        return False
                case 'program_code':
                    if len(record[field]) != 0 and not ProgramDatabase.has_program(record[field]):
                        return False
                case 'year':
                    if not StudentRecord._is_valid_year(record[field]):
                        return False
                case 'gender':
                    if not StudentRecord._is_valid_gender(record[field]):
                        return False
        return True

    @staticmethod
    def from_dict(record : dict[str, str]) -> StudentRecord:
        if not StudentRecord.is_valid(record):
            raise ValueError('invalid student record format')
        # TODO

@dataclass
class ProgramRecord:
    # Program attributes
    program_code : str
    program_name : str
    college_code : str

    @staticmethod
    def column_display_name(column : str) -> str:
        column_name_map = {
            'program_code': 'Program Code',
            'program_name': 'Program Name',
            'college_code': 'College Code'
        }
        return column_name_map.get(column, '')

    @staticmethod
    def is_valid(record : dict[str, str], check_all = True) -> bool:
        for field in ['program_code', 'program_name', 'college_code']:
            if field not in record:
                if check_all:
                    return False
                else:
                    continue
            if field == 'college_code':
                if len(record[field]) != 0 and not CollegeDatabase.has_college(record[field]):
                    return False
        return True

@dataclass
class CollegeRecord:
    # College attributes
    college_code : str
    college_name : str

    @staticmethod
    def column_display_name(column : str) -> str:
        column_name_map = {
            'college_code': 'College Code',
            'college_name': 'College Name'
        }
        return column_name_map.get(column, '')

    @staticmethod
    def is_valid(record : dict[str, str], check_all = True) -> bool:
        return True

# Handles and stores student records
class StudentDatabase:
    _path = Path(__file__).parent.parent.parent / 'data' / 'students.csv'
    _db   = GenericDatabase(_path, primary_key='id')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return StudentRecord.column_display_name(col)
    
    @classmethod
    def get_ids(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_ids

    @classmethod
    def has_id(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_id

    @classmethod
    def get_records(self, where: Union[str, Callable] = None, paged: Paged = None, sorted: Sorted = None) -> List[dict]:
        return self._db.get_records(where=where, paged=paged, sorted=sorted)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict):
        if not StudentRecord.is_valid(record):
            raise ValueError('Invalid student record format')
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict):
        if not StudentRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid student record format')
        self._db.update_records(where, updates)

    @classmethod
    def update_record(self, updates : dict, *, index : int = None, key : str = None):
        if not StudentRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid student record format')
        self._db.update_record(updates, index = index, key = key)

    @classmethod 
    def delete_records(self, where: Union[str, Callable]):
        self._db.delete_records(where)

    @classmethod
    def delete_record(self, *, index: int = None, key: str = None):
        self._db.delete_record(index = index, key = key)

# Handles and stores program records
class ProgramDatabase:
    _path = Path(__file__).parent.parent.parent / 'data' / 'programs.csv'
    _db   = GenericDatabase(_path, primary_key='program_code')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return ProgramRecord.column_display_name(col)
    
    @classmethod
    def get_programs(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_programs

    @classmethod
    def has_program(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_program

    @classmethod
    def get_records(self, where : Union[str, Callable] = None, paged : Paged = None, sorted: Sorted = None) -> List[dict]:
        return self._db.get_records(where=where, paged=paged, sorted=sorted)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict):
        if not ProgramRecord.is_valid(record):
            raise ValueError('Invalid program record format')
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict):
        if not ProgramRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid program record format')
        self._db.update_records(where, updates)
        # TODO: update student records

    @classmethod
    def update_record(self, updates : dict, *, index : int = None, key : str = None, action : ConstraintAction = ConstraintAction.Restrict):
        if not ProgramRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid program record format')
        old_program_code = self.get_record(index = index, key = key)['program_code']
        new_program_code = old_program_code
        if 'program_code' in updates:
            new_program_code = updates['program_code']
        if new_program_code != old_program_code:
            for student_record in StudentDatabase.get_records(where = f'program_code == {old_program_code}'):
                match action:
                    # renames all student record's program_code to its new name
                    case ConstraintAction.Cascade:
                        StudentDatabase.update_record({'program_code' : new_program_code}, key = student_record['id'])

                    case ConstraintAction.SetNull:
                        StudentDatabase.update_record({'program_code' : ''}, key = student_record['id'])

                    case ConstraintAction.Restrict:
                        raise ValueError('...')
        self._db.update_record(updates, index = index, key = key)

    @classmethod
    def delete_records(self, where: Union[str, Callable]):
        self._db.delete_records(where)
        # TODO handle student records

    @classmethod
    def delete_record(self, *, index: int = None, key: str = None, action : ConstraintAction = ConstraintAction.Restrict):
        program_code = self.get_record(index = index, key = key)['program_code']
        for student_record in StudentDatabase.get_records(where = f'program_code == {program_code}'):
            match action:
                # deletes all records referring to the same program_code
                case ConstraintAction.Cascade:
                    StudentDatabase.delete_record(key = student_record['id'])

                case ConstraintAction.SetNull:
                    StudentDatabase.update_record({'program_code' : ''}, key = student_record['id'])

                case ConstraintAction.Restrict:
                    raise ValueError('...')
        self._db.delete_record(index = index, key = key)

# Handles and stores college records
class CollegeDatabase:
    _path = Path(__file__).parent.parent.parent / 'data' / 'colleges.csv'
    _db   = GenericDatabase(_path, primary_key='college_code')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return CollegeRecord.column_display_name(col)
    
    @classmethod
    def get_colleges(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_colleges

    @classmethod
    def has_college(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_college

    @classmethod
    def get_records(self, where : Union[str, Callable] = None, paged: Paged = None, sorted: Sorted = None) -> List[dict]:
        return self._db.get_records(where=where, paged=paged, sorted=sorted)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict):
        if not CollegeRecord.is_valid(record):
            raise ValueError('Invalid college record format')
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict):
        if not CollegeRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid college record format')
        self._db.update_records(where, updates)

    @classmethod
    def update_record(self, updates : dict, *, index : int = None, key : str = None, action : ConstraintAction = ConstraintAction.Restrict):
        if not CollegeRecord.is_valid(updates, check_all = False):
            raise ValueError('Invalid college record format')
        old_college_code = self.get_record(index = index, key = key)['college_code']
        new_college_code = old_college_code
        if 'college_code' in updates:
            new_college_code = updates['college_code']
        if new_college_code != old_college_code:
            for program_record in ProgramDatabase.get_records(where = f'program_code == {old_college_code}'):
                match action:
                    case ConstraintAction.Cascade:
                        ProgramDatabase.update_record({'college_code' : new_college_code}, key = program_record['program_code'])

                    case ConstraintAction.SetNull:
                        ProgramDatabase.update_record({'college_code' : ''}, key = program_record['program_code'])

                    case ConstraintAction.Restrict:
                        raise ValueError('...')
        self._db.update_record(updates, index = index, key = key)

    @classmethod
    def delete_records(self, where: Union[str, Callable]):
        self._db.delete_records(where)

    @classmethod
    def delete_record(self, *, index: int = None, key: str = None, action : ConstraintAction = ConstraintAction.Restrict):
        college_code = self.get_record(index = index, key = key)['college_code']
        for program_record in ProgramDatabase.get_records(where = f'college_code == {college_code}'):
            match action:
                # deletes all records referring to the same college_code
                case ConstraintAction.Cascade:
                    ProgramDatabase.delete_record(key = program_record['program_code'], action = action)

                case ConstraintAction.SetNull:
                    ProgramDatabase.update_record({'college_code' : ''}, key = program_record['program_code'], action = action)

                case ConstraintAction.Restrict:
                    raise ValueError('...')
        self._db.delete_record(index = index, key = key)