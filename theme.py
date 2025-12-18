"""UI Theme Configuration - Easy customization of colors, fonts, and sizes."""

class Theme:
    """Theme configuration for the Intake UI."""
    
    # Colors
    BACKGROUND = '#2b2b2b'  # Dark gray background
    TEXT_PRIMARY = '#ffffff'  # White text
    TEXT_SECONDARY = '#cccccc'  # Light gray text
    
    # Button colors
    BUTTON_ADD = '#4CAF50'  # Green
    BUTTON_ADD_ACTIVE = '#2e7d32'  # Darker green when selected
    BUTTON_ADD_HOVER = '#45a049'  # Hover state
    
    BUTTON_OPEN = '#ff9800'  # Orange
    BUTTON_OPEN_ACTIVE = '#f57c00'  # Darker orange when selected
    BUTTON_OPEN_HOVER = '#fb8c00'  # Hover state
    
    BUTTON_DEDUCT = '#f44336'  # Red
    BUTTON_DEDUCT_ACTIVE = '#c62828'  # Darker red when selected
    BUTTON_DEDUCT_HOVER = '#da190b'  # Hover state
    
    BUTTON_CONFIG = '#555555'  # Gray
    BUTTON_SAVE = '#4CAF50'  # Green
    
    # Status colors
    STATUS_SUCCESS = '#4CAF50'  # Green
    STATUS_ERROR = '#f44336'  # Red
    STATUS_WARNING = '#ff9800'  # Orange
    STATUS_INFO = '#2196F3'  # Blue
    
    # Fonts
    FONT_FAMILY = 'Arial'  # Change to 'Helvetica', 'DejaVu Sans', etc.
    FONT_TITLE_SIZE = 32
    FONT_TITLE_WEIGHT = 'bold'
    
    FONT_BUTTON_SIZE = 24
    FONT_BUTTON_WEIGHT = 'bold'
    
    FONT_STATUS_SIZE = 20
    FONT_STATUS_WEIGHT = 'normal'
    
    FONT_STATUS_LARGE_SIZE = 24
    FONT_STATUS_LARGE_WEIGHT = 'bold'
    
    FONT_INFO_SIZE = 18
    FONT_INFO_WEIGHT = 'normal'
    
    FONT_CONFIG_SIZE = 14
    FONT_CONFIG_WEIGHT = 'normal'
    
    FONT_CONFIG_BUTTON_SIZE = 14
    FONT_CONFIG_BUTTON_WEIGHT = 'bold'
    
    # Sizes and spacing
    BUTTON_WIDTH = 18  # Slightly smaller to fit 3 buttons nicely
    BUTTON_HEIGHT = 3
    BUTTON_BORDER_WIDTH = 5
    
    PADDING_X = 20
    PADDING_Y = 20
    TITLE_PADDING_BOTTOM = 30
    BUTTON_PADDING = 20
    STATUS_PADDING = 20
    
    # Image settings
    PRODUCT_IMAGE_SIZE = (200, 200)  # Max size for product images
    
    # Window settings
    FULLSCREEN = True
    WINDOW_TITLE = "Intake"
    
    # Status reset delay (milliseconds)
    STATUS_RESET_DELAY = 3000
    
    # Text wrapping
    TEXT_WRAP_LENGTH = 800
    
    @classmethod
    def get_font(cls, size_key: str, weight_key: str = 'WEIGHT') -> tuple:
        """Get font tuple for tkinter."""
        size = getattr(cls, f'FONT_{size_key}_SIZE')
        weight = getattr(cls, f'FONT_{size_key}_{weight_key}', 'normal')
        return (cls.FONT_FAMILY, size, weight)
    
    @classmethod
    def get_title_font(cls) -> tuple:
        """Get title font."""
        return cls.get_font('TITLE', 'WEIGHT')
    
    @classmethod
    def get_button_font(cls) -> tuple:
        """Get button font."""
        return cls.get_font('BUTTON', 'WEIGHT')
    
    @classmethod
    def get_status_font(cls) -> tuple:
        """Get status font."""
        return cls.get_font('STATUS', 'WEIGHT')
    
    @classmethod
    def get_status_large_font(cls) -> tuple:
        """Get large status font."""
        return cls.get_font('STATUS_LARGE', 'WEIGHT')
    
    @classmethod
    def get_info_font(cls) -> tuple:
        """Get info font."""
        return cls.get_font('INFO', 'WEIGHT')
    
    @classmethod
    def get_config_font(cls) -> tuple:
        """Get config dialog font."""
        return cls.get_font('CONFIG', 'WEIGHT')
    
    @classmethod
    def get_config_button_font(cls) -> tuple:
        """Get config button font."""
        return cls.get_font('CONFIG_BUTTON', 'WEIGHT')


# Example: Light theme (uncomment to use)
# class LightTheme(Theme):
#     BACKGROUND = '#f5f5f5'
#     TEXT_PRIMARY = '#000000'
#     TEXT_SECONDARY = '#333333'
#     BUTTON_CONFIG = '#888888'

# Example: Custom theme (uncomment and modify)
# class CustomTheme(Theme):
#     BACKGROUND = '#1a1a2e'  # Dark blue
#     BUTTON_ADD = '#00d4aa'  # Teal
#     BUTTON_DEDUCT = '#ff6b6b'  # Coral red
#     FONT_FAMILY = 'Helvetica'

