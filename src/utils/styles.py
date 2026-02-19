from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

from src.utils.constants import Constants
from src.utils.font_loader import FontLoader

class Styles:
    @staticmethod 
    def page(id):
        return f"""
            #{id} {{ background-color: {Constants.BACKGROUND_COLOR}; }}
            QLabel {{ color: black; font-family: {FontLoader.get('body')}; }}
        """

    @staticmethod
    def info_label(fontSize = 12, bold = False, italic = False, color = 'black'):
        italic_str = 'italic' if italic else 'normal'
        weight_str = 'bold' if bold else 'normal'
        return f"""
            font-size: {fontSize}px; 
            color: {color}; 
            font-family: {FontLoader.get("body")}; 
            font-style: {italic_str}; 
            font-weight: {weight_str};
        """

    @staticmethod 
    def title_label(fontSize):
        return f'font-size: {fontSize}px; font-weight: bold; color: black; font-family: {FontLoader.get("title")};'
    
    @staticmethod 
    def action_button(back_color = 'black', text_color = 'white', font_size = 14):
        qcolor = QColor(back_color)
        hover_color = '#333' if qcolor.lightness() == 0 else qcolor.lighter(110).name()
        return f"""
            QPushButton {{
                background-color: {back_color};
                color: {text_color};
                font-size: {font_size}px;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
    
    @staticmethod
    def input_field(back_color = '#d9d9d9', text_color = 'black'):
        qcolor = QColor(back_color)
        hover_color = '#e6e6e6' if qcolor.lightness() > 200 else qcolor.lighter(120).name()
        return f"""
            QLineEdit {{
                background-color: {back_color};
                color: {text_color};
                border: 1px solid transparent;
                border-radius: 15px;
                padding: 10px 15px;
                font-size: 12px;
                selection-background-color: #2980b9;
            }}
            QLineEdit:hover, QLineEdit:focus {{
                background-color: {hover_color};
            }}
        """
    
    @staticmethod
    def card(id_name):
        back_color = Constants.CARD_COLOR
        # border_color = '#ccc'
        border_radius = 30
        return f"""
            #{id_name} {{
                background-color: {back_color}; 
                
                border-radius: {border_radius}px;
                padding: 20px;
            }}
        """
        # border: 2px solid {border_color};
    
    @staticmethod
    def card_shadow():
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setXOffset(10)
        shadow.setYOffset(10)
        shadow.setColor(QColor(Constants.CARD_SHADOW_COLOR))
        return shadow
    
    @staticmethod 
    def toggle_box(mini = False):
        if mini:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: #444444;      /* Inactive text color */
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 20px;
                    border-radius: 16px; /* Inner pill shape for the active state */
                    border: 1px solid transparent;
                }}
                QPushButton:hover:!checked {{
                    background-color: rgba(143, 174, 68, 0.15); /* Faint green on hover */
                    border-radius: 16px;
                    border: 1px solid rgba(143, 174, 68, 0.15);
                }}
                QPushButton:checked {{
                    background-color: #8fae44; /* Solid green active background */
                    color: white;              /* White text when active */
                    border-radius: 16px;
                    border: 1px solid #8fae44;
                }}
            """
        else:
            return f"""
                QToolButton {{
                    background-color: #f0f0f0;
                    padding: 10px 20px;
                    color: #333;
                    font-size: 14px;
                    border-radius: 20px;
                }}
                
                /* The Active State */
                QToolButton:checked {{
                    background-color: {Constants.ACTIVE_BUTTON_COLOR};
                    color: white;
                    font-weight: bold;
                    border: 2px solid {Constants.ACTIVE_BUTTON_BORDER_COLOR};
                }}
                
                /* Round the left corners of the first button */
                QToolButton:first-child{{
                    border-top-left-radius: 6px;
                    border-bottom-left-radius: 6px;
                }}
                
                /* Round the right corners of the last button */
                QToolButton:last-child {{
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                }}
                
                /* Hover Effect */
                QToolButton:hover:!checked {{
                    background-color: #e0e0e0;
                }}
            """
    
    @staticmethod
    def header():
        back_color = Constants.HEADER_COLOR
        return f"""
            #Header {{
                background-color: {Constants.HEADER_COLOR};
                padding: 20px;
                border-bottom: 1px solid #999;
            }}
        """
    
    @staticmethod
    def search_bar():
        return f"""
            QLineEdit {{
                background-color: transparent;
                font-size: 12px;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 15px;
                padding: 8px 15px;
            }}
            QLineEdit:focus {{
                border: 1px solid #93a846; /* Highlight color when typing */
                border-radius: 15px;
            }}
        """
    
    @staticmethod
    def table():
        return f"""
        QTableView {{
            background-color: transparent;
            border: none;
            outline: none;
            border-bottom: 2px solid #cccccc; /* Bottom border of the entire table */
        }}
        
        /* Individual cells */
        QTableView::item {{
            background-color: transparent;
            border: none;
            padding: 10px;
            color: #333333;
        }}

        QTableView::item:focus {{
            border: none;
            outline: none;
            background-color: transparent;
        }}

        /* The header container */
        QHeaderView {{
            background-color: transparent;
            border: none;
        }}

        /* Individual column headers */
        QHeaderView::section {{
            background-color: transparent;
            border: none;
            border-bottom: 2px solid #cccccc; /* Bottom border of the header row */
            padding: 10px;
            font-weight: bold;
            text-align: left;
            color: #666666;
        }}

        /* The tiny square where horizontal and vertical headers meet (if visible) */
        QTableCornerButton::section {{
            background-color: transparent;
            border: none;
        }}

        QScrollBar {{
            background: transparent;
            margin: 0px;
        }}

        QScrollBar::handle {{
            background: #cccccc;
            border-radius: 7px;
            border: 3px solid white;
        }}

        QScrollBar::handle:hover {{
            background: #aaaaaa;
        }}

        QScrollBar::add-page, QScrollBar::sub-page {{
            background: transparent;
        }}

        /* 2. SPECIFIC DIMENSIONS (Vertical) */
        QScrollBar:vertical {{ width: 14px; }}
        QScrollBar::handle:vertical {{ min-height: 30px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

        /* 3. SPECIFIC DIMENSIONS (Horizontal) */
        QScrollBar:horizontal {{ height: 14px; }}
        QScrollBar::handle:horizontal {{ min-width: 30px; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
    """