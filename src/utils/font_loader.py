from pathlib import Path
from PyQt6.QtGui import QFontDatabase

from .constants import Constants

class FontLoader:
    _families = {}

    @classmethod
    def load(self):
        font_map = Constants.FONT_PATHS
        for key, path in font_map.items():
            if not Path(path).exists():
                raise FileNotFoundError(f'Font file not found: {path}')
            font_id = QFontDatabase.addApplicationFont(path)
            
            if font_id == -1:
                raise Exception(f'Failed to load font: {path}')
                self._families[key] = 'Arial'
            else:
                loaded_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self._families[key] = loaded_family

    @classmethod
    def add_default(self, family_name):
        self._families['default'] = family_name

    @classmethod
    def get(self, key):
        return self._families.get(key, 'Arial')