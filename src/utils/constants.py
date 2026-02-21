from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen = True, init = False)
class Constants:
    TEXT_SECONDARY_COLOR = '#999999'

    BACKGROUND_COLOR = '#E9FF85'
    ACTIVE_BUTTON_COLOR = '#93A932'
    ACTIVE_BUTTON_BORDER_COLOR = '#687B11'
    DANGER_COLOR = '#F45742'

    CARD_COLOR = '#FFFFFF'
    CARD_SHADOW_COLOR = "#EBEBEB"

    HEADER_COLOR = '#EFFFA4'

    LOGIN_BUTTON_COLOR = '#5759D7'
    LOGOUT_BUTTON_COLOR = DANGER_COLOR

    HEADER_BUTTON_COLOR = '#E8F3B5'

    _ABS_FONT_DIR = Path(__file__).parent.parent.parent / 'assets' / 'fonts'

    FONT_PATHS = {
        'title': str(_ABS_FONT_DIR / 'Rokkitt' / 'Rokkitt-VariableFont_wght.ttf'),
        'body':  str(_ABS_FONT_DIR / 'Rethink_Sans' / 'RethinkSans-VariableFont_wght.ttf')
    }