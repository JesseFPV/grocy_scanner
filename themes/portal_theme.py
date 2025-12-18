"""Portal / Aperture Science theme for Intake."""
import os
from theme import Theme


class PortalTheme(Theme):
    """Portal/Aperture Science inspired theme with Rajdhani font."""
    
    # Portal/Aperture Science color scheme
    BACKGROUND = '#0a0a0a'  # Very dark background (almost black)
    TEXT_PRIMARY = '#ffffff'  # White text
    TEXT_SECONDARY = '#b0b0b0'  # Light gray text
    
    # Button colors - Portal style (very dark gray base with colored accents)
    # Base colors - very dark gray for better contrast with white text
    BUTTON_BASE = '#1a1a1a'  # Very dark gray base for all buttons (almost black)
    BUTTON_BASE_ACTIVE = '#2d2d2d'  # Slightly lighter gray when selected
    
    # Add button - very dark gray with blue accent
    BUTTON_ADD = '#1a1a1a'  # Very dark gray base (almost black)
    BUTTON_ADD_ACTIVE = '#2a3a4a'  # Dark gray with slight blue tint when selected
    BUTTON_ADD_HOVER = '#252525'  # Slightly lighter gray hover
    BUTTON_ADD_BORDER_ACTIVE = '#00d4ff'  # Bright cyan border when active
    
    # Open button - very dark gray with orange accent
    BUTTON_OPEN = '#1a1a1a'  # Very dark gray base (almost black)
    BUTTON_OPEN_ACTIVE = '#3a2a1a'  # Dark gray with slight orange tint when selected
    BUTTON_OPEN_HOVER = '#252525'  # Slightly lighter gray hover
    BUTTON_OPEN_BORDER_ACTIVE = '#ffc502'  # Bright yellow-orange border when active
    
    # Deduct button - very dark gray with red accent
    BUTTON_DEDUCT = '#1a1a1a'  # Very dark gray base (almost black)
    BUTTON_DEDUCT_ACTIVE = '#3a1a1a'  # Dark gray with slight red tint when selected
    BUTTON_DEDUCT_HOVER = '#252525'  # Slightly lighter gray hover
    BUTTON_DEDUCT_BORDER_ACTIVE = '#ff6060'  # Bright pink-red border when active
    
    BUTTON_CONFIG = '#1a1a1a'  # Same dark gray as other buttons
    BUTTON_CONFIG_HOVER = '#2d2d2d'  # Slightly lighter on hover
    BUTTON_SAVE = '#1a1a1a'  # Dark gray base (consistent with other buttons)
    BUTTON_SAVE_HOVER = '#2d2d2d'  # Slightly lighter on hover
    
    # Status colors
    STATUS_SUCCESS = '#00d4ff'  # Bright cyan (Portal success)
    STATUS_ERROR = '#ff3838'  # Red
    STATUS_WARNING = '#ffa502'  # Orange
    STATUS_INFO = '#00a8ff'  # Portal blue
    
    # Fonts - Rajdhani
    FONT_FAMILY = 'Rajdhani'  # Portal-style font
    FONT_TITLE_SIZE = 36
    FONT_TITLE_WEIGHT = 'bold'
    
    FONT_BUTTON_SIZE = 20
    FONT_BUTTON_WEIGHT = 'semibold'
    
    FONT_STATUS_SIZE = 18
    FONT_STATUS_WEIGHT = 'medium'
    
    FONT_STATUS_LARGE_SIZE = 24
    FONT_STATUS_LARGE_WEIGHT = 'bold'
    
    FONT_INFO_SIZE = 16
    FONT_INFO_WEIGHT = 'regular'
    
    FONT_CONFIG_SIZE = 16
    FONT_CONFIG_WEIGHT = 'regular'
    
    FONT_CONFIG_BUTTON_SIZE = 16
    FONT_CONFIG_BUTTON_WEIGHT = 'semibold'
    
    # Sizes and spacing - compact for small displays (1024x600)
    BUTTON_WIDTH = 16
    BUTTON_HEIGHT = 2
    BUTTON_BORDER_WIDTH = 2
    BUTTON_BORDER_ACTIVE_WIDTH = 3  # Thicker border when active
    
    PADDING_X = 20
    PADDING_Y = 15
    TITLE_PADDING_BOTTOM = 20
    BUTTON_PADDING = 10
    STATUS_PADDING = 10
    
    # Image settings - smaller for compact display (1024x600)
    PRODUCT_IMAGE_SIZE = (120, 120)
    
    # Window settings
    FULLSCREEN = True
    WINDOW_TITLE = "INTAKE"
    
    # Status reset delay
    STATUS_RESET_DELAY = 3000
    
    # Text wrapping
    TEXT_WRAP_LENGTH = 900
    
    # Portal-specific settings
    ACTIVE_INDICATOR_COLOR = '#00d4ff'  # Bright cyan indicator
    ACTIVE_GLOW_INTENSITY = 2  # Border thickness for glow effect
    
    @classmethod
    def load_fonts(cls):
        """Load Rajdhani fonts if available."""
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Rajdhani')
        if os.path.exists(font_path):
            try:
                import tkinter.font as tkfont
                # Try to register fonts (may not work on all systems)
                # Fonts will be used if system recognizes 'Rajdhani'
                pass
            except:
                pass
    
    @classmethod
    def get_font(cls, size_key: str, weight_key: str = 'WEIGHT') -> tuple:
        """Get font tuple for tkinter with Rajdhani."""
        size = getattr(cls, f'FONT_{size_key}_SIZE')
        weight = getattr(cls, f'FONT_{size_key}_{weight_key}', 'normal')
        
        # Map weight names to tkinter weights
        weight_map = {
            'light': 'normal',
            'regular': 'normal',
            'medium': 'normal',
            'semibold': 'bold',
            'bold': 'bold'
        }
        tk_weight = weight_map.get(weight.lower(), 'normal')
        
        return (cls.FONT_FAMILY, size, tk_weight)

