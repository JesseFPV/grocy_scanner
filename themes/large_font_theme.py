"""Large font theme for better visibility."""
from theme import Theme


class LargeFontTheme(Theme):
    """Theme with larger fonts for better readability."""
    
    # Fonts - All increased for better visibility
    FONT_TITLE_SIZE = 48  # Increased from 32
    FONT_BUTTON_SIZE = 32  # Increased from 24
    FONT_STATUS_SIZE = 28  # Increased from 20
    FONT_STATUS_LARGE_SIZE = 36  # Increased from 24
    FONT_INFO_SIZE = 24  # Increased from 18
    FONT_CONFIG_SIZE = 18  # Increased from 14
    FONT_CONFIG_BUTTON_SIZE = 18  # Increased from 14
    
    # Larger buttons for easier touch interaction
    BUTTON_WIDTH = 25  # Increased from 20
    BUTTON_HEIGHT = 4  # Increased from 3
    
    # More spacing
    PADDING_X = 30
    PADDING_Y = 30
    TITLE_PADDING_BOTTOM = 40
    BUTTON_PADDING = 30
    STATUS_PADDING = 30
    
    # Larger product images
    PRODUCT_IMAGE_SIZE = (250, 250)  # Increased from (200, 200)
    
    # Longer text wrap
    TEXT_WRAP_LENGTH = 1000  # Increased from 800

