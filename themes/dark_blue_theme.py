"""Dark blue theme example."""
from theme import Theme


class DarkBlueTheme(Theme):
    """Dark blue theme with teal and coral accents."""
    
    # Colors
    BACKGROUND = '#1a1a2e'  # Dark blue background
    TEXT_PRIMARY = '#ffffff'  # White text
    TEXT_SECONDARY = '#e0e0e0'  # Light gray text
    
    # Button colors
    BUTTON_ADD = '#00d4aa'  # Teal
    BUTTON_ADD_ACTIVE = '#00a085'  # Darker teal when selected
    BUTTON_ADD_HOVER = '#00b894'  # Hover state
    
    BUTTON_DEDUCT = '#ff6b6b'  # Coral red
    BUTTON_DEDUCT_ACTIVE = '#ee5a6f'  # Darker coral when selected
    BUTTON_DEDUCT_HOVER = '#ff5252'  # Hover state
    
    BUTTON_CONFIG = '#6c5ce7'  # Purple
    BUTTON_SAVE = '#00d4aa'  # Teal
    
    # Status colors
    STATUS_SUCCESS = '#00d4aa'  # Teal
    STATUS_ERROR = '#ff6b6b'  # Coral red
    STATUS_WARNING = '#fdcb6e'  # Yellow
    STATUS_INFO = '#74b9ff'  # Light blue

