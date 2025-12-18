"""Light theme example for Intake."""
from theme import Theme


class LightTheme(Theme):
    """Light theme with dark text on light background."""
    
    # Colors
    BACKGROUND = '#f5f5f5'  # Light gray background
    TEXT_PRIMARY = '#000000'  # Black text
    TEXT_SECONDARY = '#333333'  # Dark gray text
    
    # Button colors
    BUTTON_ADD = '#4CAF50'  # Green
    BUTTON_ADD_ACTIVE = '#2e7d32'  # Darker green when selected
    BUTTON_ADD_HOVER = '#45a049'  # Hover state
    
    BUTTON_DEDUCT = '#f44336'  # Red
    BUTTON_DEDUCT_ACTIVE = '#c62828'  # Darker red when selected
    BUTTON_DEDUCT_HOVER = '#da190b'  # Hover state
    
    BUTTON_CONFIG = '#888888'  # Gray
    BUTTON_SAVE = '#4CAF50'  # Green
    
    # Status colors
    STATUS_SUCCESS = '#2e7d32'  # Darker green
    STATUS_ERROR = '#c62828'  # Darker red
    STATUS_WARNING = '#ff9800'  # Orange
    STATUS_INFO = '#2196F3'  # Blue

