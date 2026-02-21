from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union, Callable, Optional, Iterator, List
import pandas as pd

from src.model.errors import ArgumentError, DatabaseError, DatabaseErrorKind
from src.model.entries import *

class ConstraintAction(Enum):
    Cascade  = 0 # automatically updates/deletes related records when the referenced record is updated/deleted
    SetNull  = 1 # sets the value to null (or a default) when the related record is deleted/updated
    Restrict = 2 # prevents the change and raises an error    

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

    # Requests a list that yields specific page of 'size' records
    @staticmethod
    def Specific(index: int, size: int):
        return Paged(size=size, index=index)

    # Requests a generator that yields pages of 'size' records each
    @staticmethod
    def Stream(size: int):
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
        if where is not None:
            if isinstance(where, str):
                try:
                    return len(self.df.query(where))
                except Exception as e:
                    raise DatabaseError(DatabaseErrorKind.INVALID_QUERY, 
                                        f'Invalid query: \'{where}\'')
            elif callable(where):
                return len(self.df[self.df.apply(where, axis = 1)])
        else:
            return len(self.df)
        
    def get_columns(self) -> List[str]:
        return self.df.columns.tolist()
    
    def get_keys(self) -> List[str]:
        return self.df[self.primary_key].astype(str).tolist() if self.primary_key else []
    
    def has_key(self, key: str) -> bool:
        if not self.primary_key:
            raise DatabaseError(DatabaseErrorKind.UNDEFINED_PRIMARY_KEY)
        return key in self.df[self.primary_key].astype(str).values
    
    def get_records_as_dataframe(self, 
                                 where: Union[str, Callable] = None,
                                 sorted: Optional[Sorted] = None,
                                 page: Optional[Paged] = None) -> pd.DataFrame:
        temp_df = self.df.copy()
        if where is not None:
            if isinstance(where, str):
                try:
                    temp_df = temp_df.query(where)
                except Exception as e:
                    raise DatabaseError(DatabaseErrorKind.INVALID_QUERY,
                                        f'Invalid query: \'{where}\'')
            elif callable(where):
                temp_df = temp_df[temp_df.apply(where, axis=1)]
        if sorted is not None:
            if sorted.column in temp_df.columns:
                temp_df = temp_df.sort_values(by = sorted.column, ascending = sorted.ascending)
            else:
                raise DatabaseError(DatabaseErrorKind.HEADER_NAME_NOT_FOUND,
                                    f'Column \'{sorted.column}\' does not exist for sorting')
        if page is not None and page.index is not None:
            start = (page.index - 1) * page.size
            end = start + page.size
            temp_df = temp_df.iloc[start:end]
        return temp_df

    def get_records(self, 
                    where: Union[str, Callable] = None, 
                    sorted: Optional[Sorted] = None, 
                    paged: Optional[Paged] = None) -> Union[List[dict], Iterator[List[dict]]]:
        temp_df = self.df.copy() # Work on a copy to avoid sorting the actual DB
        if where is not None:
            if isinstance(where, str):
                try:
                    temp_df = temp_df.query(where)
                except Exception as e:
                    raise DatabaseError(DatabaseErrorKind.INVALID_QUERY,
                                        f'Invalid query: \'{where}\'')
            elif callable(where):
                temp_df = temp_df[temp_df.apply(where, axis=1)]
        if sorted is not None:
            if sorted.column in temp_df.columns:
                temp_df = temp_df.sort_values(by = sorted.column, ascending = sorted.ascending)
            else:
                raise DatabaseError(DatabaseErrorKind.HEADER_NAME_NOT_FOUND,
                                    f'Column \'{sorted.column}\' does not exist for sorting')
        if paged is not None:
            if paged.index is not None:
                start = (paged.index - 1) * paged.size
                end = start + paged.size
                return temp_df.iloc[start:end].to_dict('records')
            else:
                def chunk_generator():
                    total = len(temp_df)
                    for start in range(0, total, paged.size):
                        yield temp_df.iloc[start : start + paged.size].to_dict('records')
                return chunk_generator()
        return temp_df.to_dict('records')
    
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        if index is not None and key is not None:
            raise ArgumentError('Provide either \'index\' or \'key\', not both')
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise ArgumentError('Record index out of range')
            return self.df.iloc[index].to_dict()
        elif key is not None:
            if not self.primary_key:
                raise DatabaseError(DatabaseErrorKind.UNDEFINED_PRIMARY_KEY)
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise DatabaseError(DatabaseErrorKind.NO_KEY, 
                                    f'An entry with key \'{key}\' does not exist')
            return filtered_df.iloc[0].to_dict()
        else:
            raise ArgumentError('Index must be an integer or string')

    def add_record(self, record: dict):
        if self.df.empty:
            self.df = pd.DataFrame([record])
            if not self.primary_key: self.primary_key = list(record.keys())[0]
            self.modified = True
            return
        if self.primary_key:
            pk_val = record.get(self.primary_key)
            if pk_val and str(pk_val) in self.df[self.primary_key].astype(str).values:
                raise DatabaseError(DatabaseErrorKind.DUPLICATE_KEY,
                                    f'The key \'{pk_val}\' already exists')
        self.df = pd.concat([self.df, pd.DataFrame([record])], ignore_index=True)
        self.modified = True
    
    def update_records(self, where: Union[str, Callable], updates: dict):
        # Update multiple rows based on a condition.
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
        if index is not None and key is not None:
            raise ArgumentError('Provide either \'index\' or \'key\', not both')
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise ArgumentError('Record index out of range')
        elif key is not None:
            if not self.primary_key:
                raise DatabaseError(DatabaseErrorKind.UNDEFINED_PRIMARY_KEY)
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise DatabaseError(DatabaseErrorKind.NO_KEY, 
                                    f'An entry with key \'{key}\' does not exist')
            index = filtered_df.index[0]
        if self.primary_key and self.primary_key in updates:
            new_pk = str(updates[self.primary_key])
            current_pk = str(self.df.at[index, self.primary_key])            
            if new_pk != current_pk:
                if new_pk in self.df[self.primary_key].astype(str).values:
                    raise DatabaseError(DatabaseErrorKind.DUPLICATE_KEY)
        idx = index if index is not None else key
        for updated_key, updated_value in updates.items():
            if updated_key in self.df.columns:
                self.df.at[idx, updated_key] = updated_value
        self.modified = True

    def delete_records(self, where: Union[str, Callable]):
        # Delete multiple rows based on a condition
        if self.df.empty: return
        if isinstance(where, str):
            mask = self.df.eval(where)
            self.df = self.df[~mask]
        elif callable(where):
            mask = self.df.apply(where, axis = 1)
            self.df = self.df[~mask]
        self.df.reset_index(drop = True, inplace = True)
        self.modified = True

    def delete_record(self, *, index: int = None, key: str = None):
        # Delete a single row by its specific index or a key value
        if index is not None and key is not None:
            raise ArgumentError('Provide either \'index\' or \'key\', not both')
        if index is not None:
            if index < 0 or index >= len(self.df):
                raise ArgumentError('Record index out of range')
            self.df = self.df.drop(index).reset_index(drop = True)
        elif key is not None:
            if not self.primary_key:
                raise DatabaseError(DatabaseErrorKind.UNDEFINED_PRIMARY_KEY)
            filtered_df = self.df[self.df[self.primary_key].astype(str) == key]
            if filtered_df.empty:
                raise DatabaseError(DatabaseErrorKind.NO_KEY, 
                                    f'An entry with key \'{key}\' does not exist')
            self.df = self.df[self.df[self.primary_key].astype(str) != key].reset_index(drop = True)
        self.modified = True

    def save(self):
        if self.modified:
            self.df.to_csv(self.file_path, index=False)
            self.modified = False

# Handles and stores student records
class StudentDirectory:
    _path = Path(__file__).parent.parent.parent / 'data' / 'students.csv'
    _db   = GenericDatabase(_path, primary_key = 'id')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return StudentEntry.get_fields()[col].display_name
    
    @classmethod
    def get_ids(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_ids

    @classmethod
    def has_id(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_id

    @classmethod
    def get_records(self, where: Union[str, Callable] = None, sorted: Sorted = None, paged: Paged = None) -> List[dict]:
        return self._db.get_records(where = where, sorted = sorted, paged = paged)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict[str, str]):
        StudentEntry.validate_entry(record, requires_all = True, program_directory = ProgramDirectory)
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict[str, str]):
        StudentEntry.validate_entry(updates, requires_all = False, program_directory = ProgramDirectory)
        self._db.update_records(where, updates)

    @classmethod
    def update_record(self, updates : dict[str, str], *, index : int = None, key : str = None):
        StudentEntry.validate_entry(updates, requires_all = False, program_directory = ProgramDirectory)
        self._db.update_record(updates, index = index, key = key)

    @classmethod 
    def delete_records(self, where: Union[str, Callable]):
        self._db.delete_records(where)

    @classmethod
    def delete_record(self, *, index: int = None, key: str = None):
        self._db.delete_record(index = index, key = key)

# Handles and stores program records
class ProgramDirectory:
    _path = Path(__file__).parent.parent.parent / 'data' / 'programs.csv'
    _db   = GenericDatabase(_path, primary_key = 'program_code')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return ProgramEntry.get_fields()[col].display_name
    
    @classmethod
    def get_programs(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_programs

    @classmethod
    def has_program(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_program

    @classmethod
    def get_records(self, where : Union[str, Callable] = None, sorted : Sorted = None, paged : Paged = None) -> List[dict]:
        return self._db.get_records(where = where, sorted = sorted, paged = paged)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict[str, str]):
        ProgramEntry.validate_entry(record, requires_all = True, college_directory = CollegeDirectory)
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict[str, str]):
        ProgramEntry.validate_entry(updates, requires_all = False, college_directory = CollegeDirectory)
        self._db.update_records(where, updates)
        # TODO: update student records

    @classmethod
    def update_record(self, updates : dict[str, str], *, index : int = None, key : str = None, action : ConstraintAction = ConstraintAction.Restrict):
        ProgramEntry.validate_entry(updates, requires_all = False, college_directory = CollegeDirectory)
        old_program_code = self.get_record(index = index, key = key)['program_code']
        new_program_code = old_program_code
        if 'program_code' in updates:
            new_program_code = updates['program_code']
        if new_program_code != old_program_code:
            for student_record in StudentDirectory.get_records(where = f'program_code == {old_program_code}'):
                match action:
                    # renames all student record's program_code to its new name
                    case ConstraintAction.Cascade:
                        StudentDirectory.update_record({'program_code' : new_program_code}, key = student_record['id'])

                    case ConstraintAction.SetNull:
                        StudentDirectory.update_record({'program_code' : ''}, key = student_record['id'])

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
        for student_record in StudentDirectory.get_records(where = f'program_code == {program_code}'):
            match action:
                # deletes all records referring to the same program_code
                case ConstraintAction.Cascade:
                    StudentDirectory.delete_record(key = student_record['id'])

                case ConstraintAction.SetNull:
                    StudentDirectory.update_record({'program_code' : ''}, key = student_record['id'])

                case ConstraintAction.Restrict:
                    raise ValueError('...')
        self._db.delete_record(index = index, key = key)

# Handles and stores college records
class CollegeDirectory:
    _path = Path(__file__).parent.parent.parent / 'data' / 'colleges.csv'
    _db   = GenericDatabase(_path, primary_key = 'college_code')

    @classmethod
    def get_count(self, where: Union[str, Callable] = None) -> int:
        return self._db.get_count(where)
    
    @classmethod
    def get_columns(self) -> List[str]:
        return self._db.get_columns()
    
    @classmethod
    def get_column_display_name(self, col : str) -> str:
        return CollegeEntry.get_fields()[col].display_name
    
    @classmethod
    def get_colleges(self) -> List[str]:
        return self._db.get_keys()
    
    get_keys = get_colleges

    @classmethod
    def has_college(self, key: str) -> bool:
        return self._db.has_key(str)
    
    has_key = has_college

    @classmethod
    def get_records(self, where : Union[str, Callable] = None, sorted: Sorted = None, paged : Paged = None) -> List[dict]:
        return self._db.get_records(where = where, sorted = sorted, paged = paged)
    
    @classmethod 
    def get_record(self, *, index : int = None, key : str = None) -> dict:
        return self._db.get_record(index = index, key = key)
    
    @classmethod 
    def add_record(self, record : dict[str, str]):
        CollegeEntry.validate_entry(record, requires_all = True)
        self._db.add_record(record)

    @classmethod
    def update_records(self, where: Union[str, Callable], updates: dict[str, str]):
        CollegeEntry.validate_entry(updates, requires_all = False)
        self._db.update_records(where, updates)

    @classmethod
    def update_record(self, updates : dict[str, str], *, index : int = None, key : str = None, action : ConstraintAction = ConstraintAction.Restrict):
        CollegeEntry.validate_entry(updates, requires_all = False)
        old_college_code = self.get_record(index = index, key = key)['college_code']
        new_college_code = old_college_code
        if 'college_code' in updates:
            new_college_code = updates['college_code']
        if new_college_code != old_college_code:
            for program_record in ProgramDirectory.get_records(where = f'program_code == {old_college_code}'):
                match action:
                    case ConstraintAction.Cascade:
                        ProgramDirectory.update_record({'college_code' : new_college_code}, key = program_record['program_code'])

                    case ConstraintAction.SetNull:
                        ProgramDirectory.update_record({'college_code' : ''}, key = program_record['program_code'])

                    case ConstraintAction.Restrict:
                        raise ValueError('...')
        self._db.update_record(updates, index = index, key = key)

    @classmethod
    def delete_records(self, where: Union[str, Callable]):
        self._db.delete_records(where)

    @classmethod
    def delete_record(self, *, index: int = None, key: str = None, action : ConstraintAction = ConstraintAction.Restrict):
        college_code = self.get_record(index = index, key = key)['college_code']
        for program_record in ProgramDirectory.get_records(where = f'college_code == {college_code}'):
            match action:
                # deletes all records referring to the same college_code
                case ConstraintAction.Cascade:
                    ProgramDirectory.delete_record(key = program_record['program_code'], action = action)

                case ConstraintAction.SetNull:
                    ProgramDirectory.update_record({'college_code' : ''}, key = program_record['program_code'], action = action)

                case ConstraintAction.Restrict:
                    raise ValueError('...')
        self._db.delete_record(index = index, key = key)