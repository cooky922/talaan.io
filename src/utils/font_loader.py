import os
from PyQt6.QtGui import QFontDatabase

from .constants import Constants

class FontLoader:
    _families = {}

    @staticmethod
    def load():
        font_map = Constants.FONT_PATHS
        for key, path in font_map.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f'Font file not found: {path}')
            font_id = QFontDatabase.addApplicationFont(path)
            
            if font_id == -1:
                raise Exception(f'Failed to load font: {path}')
                FontLoader._families[key] = 'Arial'
            else:
                loaded_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                FontLoader._families[key] = loaded_family

    @staticmethod
    def get(key):
        return FontLoader._families.get(key, 'Arial')