import os
from PyQt6.QtGui import QIcon

class IconLoader:
    _icons = {}

    @staticmethod
    def load():
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'images', 'icons')
        for file in os.listdir(icon_dir):
            if file.endswith('.svg'):
                name = os.path.splitext(file)[0]
                IconLoader._icons[name] = QIcon(os.path.join(icon_dir, file))
    
    @staticmethod
    def get(name):
        return IconLoader._icons.get(name)