"""Touch-friendly GUI for Intake."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
import threading
from typing import Optional
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import base64
from config import Config
from grocy_api import GrocyAPI
from onscreen_keyboard import OnScreenKeyboard
from icon_loader import get_icon_loader
# from theme import Theme
# Portal theme - modern Aperture Science style
from themes.portal_theme import PortalTheme as Theme


def load_custom_fonts(root: tk.Tk):
    """Load custom fonts (Rajdhani) locally - similar to CSS @font-face."""
    import platform
    import shutil
    
    font_dir = os.path.join(os.path.dirname(__file__), 'themes', 'fonts', 'Rajdhani')
    font_loaded = False
    
    if os.path.exists(font_dir):
        try:
            # Determine user font directory based on OS (like CSS @font-face)
            if platform.system() == 'Darwin':  # macOS
                user_font_dir = os.path.expanduser('~/Library/Fonts')
            elif platform.system() == 'Linux':
                user_font_dir = os.path.expanduser('~/.fonts')
            elif platform.system() == 'Windows':
                user_font_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
            else:
                user_font_dir = None
            
            # Copy fonts to user font directory (no admin rights needed)
            if user_font_dir:
                os.makedirs(user_font_dir, exist_ok=True)
                
                for font_file in os.listdir(font_dir):
                    if font_file.endswith('.ttf'):
                        source_path = os.path.join(font_dir, font_file)
                        dest_path = os.path.join(user_font_dir, font_file)
                        
                        # Only copy if not already present (like CSS font caching)
                        if not os.path.exists(dest_path):
                            try:
                                shutil.copy2(source_path, dest_path)
                                print(f"✓ Installed font: {font_file}")
                            except Exception as e:
                                print(f"Could not install font {font_file}: {e}")
                
                # On macOS, fonts need a moment to be registered
                # Force font cache refresh
                import time
                time.sleep(0.5)
            
            # Refresh font list and check if Rajdhani is now available
            root.update_idletasks()
            available_fonts = list(tkfont.families())
            
            if 'Rajdhani' in available_fonts:
                font_loaded = True
                print("✓ Rajdhani font loaded successfully!")
            else:
                # Try alternative: use font file directly (works on some systems)
                try:
                    regular_font_path = os.path.join(font_dir, 'Rajdhani-Regular.ttf')
                    if os.path.exists(regular_font_path):
                        test_font = tkfont.Font(family='Rajdhani', size=12)
                        if 'Rajdhani' in str(test_font.actual().get('family', '')):
                            font_loaded = True
                            print("✓ Rajdhani font loaded via direct file access!")
                except:
                    pass
                
        except Exception as e:
            print(f"Font loading error: {e}")
    
    # Final check and fallback
    if not font_loaded:
        available_fonts = list(tkfont.families())
        if 'Rajdhani' not in available_fonts:
            # Use a fallback font that's similar
            fallback_fonts = ['Helvetica Neue', 'Helvetica', 'Arial', 'DejaVu Sans']
            for fallback in fallback_fonts:
                if fallback in available_fonts:
                    Theme.FONT_FAMILY = fallback
                    break
            print(f"⚠ Rajdhani font not found. Using fallback: {Theme.FONT_FAMILY}")
            print("💡 Tip: Restart the application to use Rajdhani font after first installation.")


def build_grocy_image_urls(base_url: str, picture_file_name: str, product_id: Optional[int] = None, api_key: Optional[str] = None) -> list:
    """
    Build list of possible Grocy image URLs to try.
    Grocy uses base64-encoded filenames in the URL path.
    
    Args:
        base_url: Base URL of Grocy instance
        picture_file_name: The picture filename from product data
        product_id: Optional product ID
        api_key: Optional API key for query parameter
    
    Returns:
        List of URLs to try in order
    """
    urls = []
    
    if not picture_file_name:
        return urls
    
    # Base64 encode the filename (Grocy uses base64-encoded filenames in URLs)
    try:
        # Encode filename to base64 (bytes -> base64 string)
        encoded_filename = base64.b64encode(picture_file_name.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"  Warning: Could not base64 encode filename: {e}")
        encoded_filename = picture_file_name  # Fallback to original
    
    # Build query parameters
    query_params = "force_serve_as=picture&best_fit_width=400"
    if api_key:
        query_params += f"&GROCY-API-KEY={api_key}"
    
    # Primary URL format (base64 encoded filename with query params)
    urls.append(f"{base_url}/api/files/productpictures/{encoded_filename}?{query_params}")
    
    # Alternative: without query params
    urls.append(f"{base_url}/api/files/productpictures/{encoded_filename}")
    
    # Try with product ID in path
    if product_id:
        urls.append(f"{base_url}/api/files/productpictures/{product_id}/{encoded_filename}?{query_params}")
        urls.append(f"{base_url}/api/files/productpictures/{product_id}/{encoded_filename}")
    
    # Fallback: try original filename (not base64 encoded) - for older Grocy versions
    urls.append(f"{base_url}/api/files/productpictures/{picture_file_name}?{query_params}")
    urls.append(f"{base_url}/api/files/productpictures/{picture_file_name}")
    
    if product_id:
        urls.append(f"{base_url}/api/files/productpictures/{product_id}/{picture_file_name}?{query_params}")
        urls.append(f"{base_url}/api/files/productpictures/{product_id}/{picture_file_name}")
    
    # Try without /api/ prefix
    urls.append(f"{base_url}/files/productpictures/{encoded_filename}?{query_params}")
    urls.append(f"{base_url}/files/productpictures/{encoded_filename}")
    
    return urls


class GrocyScannerUI:
    """Main UI class for Intake."""
    
    def __init__(self, root: tk.Tk, config: Config):
        self.root = root
        self.config = config
        self.grocy_api: Optional[GrocyAPI] = None
        self.current_action: Optional[str] = None  # 'add', 'open', or 'deduct'
        self.scanning = False
        
        # Load custom fonts (Rajdhani)
        load_custom_fonts(root)
        
        # Setup window
        self.root.title(Theme.WINDOW_TITLE)
        self.root.attributes('-fullscreen', Theme.FULLSCREEN)  # Fullscreen for Raspberry Pi
        self.root.configure(bg=Theme.BACKGROUND)
        
        # Hide cursor for touch-only interface
        self.root.config(cursor="none")
        
        # Ensure window can receive keyboard input (important for barcode scanner)
        self.root.focus_set()
        self.root.focus_force()  # Force focus to ensure keyboard input works
        
        # Keep focus on root window for barcode scanner input
        self.root.bind('<FocusOut>', lambda e: self.root.focus_force())
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        
        self.setup_ui()
        
        # Initialize API if configured
        if self.config.is_configured():
            self.grocy_api = GrocyAPI(self.config)
            if not self.grocy_api.test_connection():
                messagebox.showerror("Connection Error", 
                                    "Could not connect to Grocy. Please check your configuration.")
                self._setup_config_page()
        else:
            self._setup_config_page()
    
    def setup_ui(self):
        """Setup the main UI components."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=Theme.BACKGROUND)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=Theme.PADDING_X, pady=Theme.PADDING_Y)
        
        # Page management
        self.current_page = 'main'
        self.search_page_frame: Optional[tk.Frame] = None
        self.product_detail_frame: Optional[tk.Frame] = None
        self.config_page_frame: Optional[tk.Frame] = None
        self.search_results: list = []
        self.hide_out_of_stock: bool = False  # Toggle for hiding out-of-stock products
        self.selected_product_group: Optional[int] = None  # Selected product group filter
        self.product_group_buttons: dict = {}  # Store product group filter buttons
        
        self._setup_main_page()
    
    def _clear_pages(self):
        """Clear all page frames except main."""
        if self.search_page_frame:
            self.search_page_frame.destroy()
            self.search_page_frame = None
        if self.product_detail_frame:
            self.product_detail_frame.destroy()
            self.product_detail_frame = None
        if self.config_page_frame:
            self.config_page_frame.destroy()
            self.config_page_frame = None
    
    def _setup_main_page(self):
        """Setup the main scanning page."""
        # Clear any existing pages
        self._clear_pages()
        self.current_page = 'main'
        
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        main_frame = self.main_frame
        
        # Search bar (initially hidden)
        self.search_frame = tk.Frame(main_frame, bg=Theme.BACKGROUND)
        self.search_entry = tk.Entry(
            self.search_frame,
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
            insertbackground='white',
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Search icon
        icon_loader = get_icon_loader()
        search_icon = icon_loader.load_icon('search', size=(24, 24), color='white')
        if search_icon:
            search_button = tk.Label(
                self.search_frame,
                image=search_icon,
                bg=Theme.BUTTON_ADD,
            )
            search_button.image = search_icon  # Keep reference
        else:
            # Fallback to text if icon not available
            search_button = tk.Label(
                self.search_frame,
                text="SEARCH",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_ADD,
                fg='white',
            )
        search_button.pack(side=tk.LEFT, padx=5)
        search_button.bind('<Button-1>', lambda e: self._perform_search())
        
        # Title with Portal-style accent line
        title_container = tk.Frame(main_frame, bg=Theme.BACKGROUND)
        title_container.pack(pady=(0, Theme.TITLE_PADDING_BOTTOM // 2))
        
        # Accent line above title (Portal style)
        accent_line = tk.Frame(title_container, bg=getattr(Theme, 'ACTIVE_INDICATOR_COLOR', Theme.STATUS_SUCCESS), height=3)
        accent_line.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            title_container,
            text=Theme.WINDOW_TITLE,
            font=Theme.get_title_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        title_label.pack()
        
        # Action buttons frame
        buttons_frame = tk.Frame(main_frame, bg=Theme.BACKGROUND)
        buttons_frame.pack(pady=(Theme.BUTTON_PADDING, Theme.BUTTON_PADDING // 2))
        
        # Button containers for active indicator
        self.add_button_frame = tk.Frame(buttons_frame, bg=Theme.BACKGROUND, width=Theme.BUTTON_WIDTH*10, height=Theme.BUTTON_HEIGHT*20)
        self.open_button_frame = tk.Frame(buttons_frame, bg=Theme.BACKGROUND, width=Theme.BUTTON_WIDTH*10, height=Theme.BUTTON_HEIGHT*20)
        self.deduct_button_frame = tk.Frame(buttons_frame, bg=Theme.BACKGROUND, width=Theme.BUTTON_WIDTH*10, height=Theme.BUTTON_HEIGHT*20)
        
        # Active indicator frames (will show when button is active) - Portal style bright accent line
        indicator_color_add = getattr(Theme, 'BUTTON_ADD_BORDER_ACTIVE', Theme.BUTTON_ADD)
        indicator_color_open = getattr(Theme, 'BUTTON_OPEN_BORDER_ACTIVE', Theme.BUTTON_OPEN)
        indicator_color_deduct = getattr(Theme, 'BUTTON_DEDUCT_BORDER_ACTIVE', Theme.BUTTON_DEDUCT)
        
        self.add_indicator = tk.Frame(self.add_button_frame, bg=indicator_color_add, height=5)
        self.open_indicator = tk.Frame(self.open_button_frame, bg=indicator_color_open, height=5)
        self.deduct_indicator = tk.Frame(self.deduct_button_frame, bg=indicator_color_deduct, height=5)
        
        # Add to Stock button - Use Frame-based approach for macOS compatibility
        # Pack indicator first (will be hidden initially)
        self.add_indicator.pack(fill=tk.X, pady=(0, 2))
        self.add_indicator.pack_forget()  # Hide initially
        
        add_bg_frame = tk.Frame(self.add_button_frame, bg=Theme.BUTTON_ADD)
        # Create container for icon and text
        add_content_frame = tk.Frame(add_bg_frame, bg=Theme.BUTTON_ADD)
        add_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load plus icon
        icon_loader = get_icon_loader()
        plus_icon = icon_loader.load_icon('plus', size=(28, 28), color='white')
        if plus_icon:
            add_icon_label = tk.Label(
                add_content_frame,
                image=plus_icon,
                bg=Theme.BUTTON_ADD
            )
            add_icon_label.image = plus_icon  # Keep reference
            add_icon_label.pack(pady=(0, 5))
        
        self.add_button = tk.Label(
            add_content_frame,
            text="ADD TO STOCK",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_ADD,
            fg='white',
        )
        self.add_button.pack()
        add_bg_frame.pack(fill=tk.BOTH, expand=True)
        # Bind click events
        self.add_button.bind('<Button-1>', lambda e: self.set_action('add'))
        add_bg_frame.bind('<Button-1>', lambda e: self.set_action('add'))
        # Hover effect
        def add_enter(e): 
            add_bg_frame.config(bg=Theme.BUTTON_ADD_HOVER)
            self.add_button.config(bg=Theme.BUTTON_ADD_HOVER)
            add_content_frame.config(bg=Theme.BUTTON_ADD_HOVER)
            if plus_icon:
                add_icon_label.config(bg=Theme.BUTTON_ADD_HOVER)
        def add_leave(e): 
            add_bg_frame.config(bg=Theme.BUTTON_ADD)
            self.add_button.config(bg=Theme.BUTTON_ADD)
            add_content_frame.config(bg=Theme.BUTTON_ADD)
            if plus_icon:
                add_icon_label.config(bg=Theme.BUTTON_ADD)
        self.add_button.bind('<Enter>', add_enter)
        self.add_button.bind('<Leave>', add_leave)
        add_bg_frame.bind('<Enter>', add_enter)
        add_bg_frame.bind('<Leave>', add_leave)
        add_content_frame.bind('<Enter>', add_enter)
        add_content_frame.bind('<Leave>', add_leave)
        if plus_icon:
            add_icon_label.bind('<Enter>', add_enter)
            add_icon_label.bind('<Leave>', add_leave)
        self.add_bg_frame = add_bg_frame  # Store reference
        self.add_button_frame.pack(side=tk.LEFT, padx=Theme.BUTTON_PADDING)
        
        # Open Product button - Use Frame-based approach for macOS compatibility
        # Pack indicator first (will be hidden initially)
        self.open_indicator.pack(fill=tk.X, pady=(0, 2))
        self.open_indicator.pack_forget()  # Hide initially
        
        open_bg_frame = tk.Frame(self.open_button_frame, bg=Theme.BUTTON_OPEN)
        # Create container for icon and text
        open_content_frame = tk.Frame(open_bg_frame, bg=Theme.BUTTON_OPEN)
        open_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load box icon
        icon_loader = get_icon_loader()
        box_icon = icon_loader.load_icon('box', size=(28, 28), color='white')
        if box_icon:
            open_icon_label = tk.Label(
                open_content_frame,
                image=box_icon,
                bg=Theme.BUTTON_OPEN
            )
            open_icon_label.image = box_icon  # Keep reference
            open_icon_label.pack(pady=(0, 5))
        
        self.open_button = tk.Label(
            open_content_frame,
            text="OPEN PRODUCT",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_OPEN,
            fg='white',
        )
        self.open_button.pack()
        open_bg_frame.pack(fill=tk.BOTH, expand=True)
        # Bind click events
        self.open_button.bind('<Button-1>', lambda e: self.set_action('open'))
        open_bg_frame.bind('<Button-1>', lambda e: self.set_action('open'))
        # Hover effect
        def open_enter(e): 
            open_bg_frame.config(bg=Theme.BUTTON_OPEN_HOVER)
            self.open_button.config(bg=Theme.BUTTON_OPEN_HOVER)
            open_content_frame.config(bg=Theme.BUTTON_OPEN_HOVER)
            if box_icon:
                open_icon_label.config(bg=Theme.BUTTON_OPEN_HOVER)
        def open_leave(e): 
            open_bg_frame.config(bg=Theme.BUTTON_OPEN)
            self.open_button.config(bg=Theme.BUTTON_OPEN)
            open_content_frame.config(bg=Theme.BUTTON_OPEN)
            if box_icon:
                open_icon_label.config(bg=Theme.BUTTON_OPEN)
        self.open_button.bind('<Enter>', open_enter)
        self.open_button.bind('<Leave>', open_leave)
        open_bg_frame.bind('<Enter>', open_enter)
        open_bg_frame.bind('<Leave>', open_leave)
        open_content_frame.bind('<Enter>', open_enter)
        open_content_frame.bind('<Leave>', open_leave)
        if box_icon:
            open_icon_label.bind('<Enter>', open_enter)
            open_icon_label.bind('<Leave>', open_leave)
        self.open_bg_frame = open_bg_frame  # Store reference
        self.open_button_frame.pack(side=tk.LEFT, padx=Theme.BUTTON_PADDING)
        
        # Deduct from Stock button - Use Frame-based approach for macOS compatibility
        # Pack indicator first (will be hidden initially)
        self.deduct_indicator.pack(fill=tk.X, pady=(0, 2))
        self.deduct_indicator.pack_forget()  # Hide initially
        
        deduct_bg_frame = tk.Frame(self.deduct_button_frame, bg=Theme.BUTTON_DEDUCT)
        # Create container for icon and text
        deduct_content_frame = tk.Frame(deduct_bg_frame, bg=Theme.BUTTON_DEDUCT)
        deduct_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load minus icon
        icon_loader = get_icon_loader()
        minus_icon = icon_loader.load_icon('minus', size=(28, 28), color='white')
        if minus_icon:
            deduct_icon_label = tk.Label(
                deduct_content_frame,
                image=minus_icon,
                bg=Theme.BUTTON_DEDUCT
            )
            deduct_icon_label.image = minus_icon  # Keep reference
            deduct_icon_label.pack(pady=(0, 5))
        
        self.deduct_button = tk.Label(
            deduct_content_frame,
            text="DEDUCT STOCK",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_DEDUCT,
            fg='white',
        )
        self.deduct_button.pack()
        deduct_bg_frame.pack(fill=tk.BOTH, expand=True)
        # Bind click events
        self.deduct_button.bind('<Button-1>', lambda e: self.set_action('deduct'))
        deduct_bg_frame.bind('<Button-1>', lambda e: self.set_action('deduct'))
        # Hover effect
        def deduct_enter(e): 
            deduct_bg_frame.config(bg=Theme.BUTTON_DEDUCT_HOVER)
            self.deduct_button.config(bg=Theme.BUTTON_DEDUCT_HOVER)
            deduct_content_frame.config(bg=Theme.BUTTON_DEDUCT_HOVER)
            if minus_icon:
                deduct_icon_label.config(bg=Theme.BUTTON_DEDUCT_HOVER)
        def deduct_leave(e): 
            deduct_bg_frame.config(bg=Theme.BUTTON_DEDUCT)
            self.deduct_button.config(bg=Theme.BUTTON_DEDUCT)
            deduct_content_frame.config(bg=Theme.BUTTON_DEDUCT)
            if minus_icon:
                deduct_icon_label.config(bg=Theme.BUTTON_DEDUCT)
        self.deduct_button.bind('<Enter>', deduct_enter)
        self.deduct_button.bind('<Leave>', deduct_leave)
        deduct_bg_frame.bind('<Enter>', deduct_enter)
        deduct_bg_frame.bind('<Leave>', deduct_leave)
        deduct_content_frame.bind('<Enter>', deduct_enter)
        deduct_content_frame.bind('<Leave>', deduct_leave)
        if minus_icon:
            deduct_icon_label.bind('<Enter>', deduct_enter)
            deduct_icon_label.bind('<Leave>', deduct_leave)
        self.deduct_bg_frame = deduct_bg_frame  # Store reference
        self.deduct_button_frame.pack(side=tk.LEFT, padx=Theme.BUTTON_PADDING)
        
        # Status frame - use fill=X instead of BOTH to leave room for keyboard
        self.status_frame = tk.Frame(main_frame, bg=Theme.BACKGROUND)
        self.status_frame.pack(fill=tk.X, pady=Theme.STATUS_PADDING)
        
        # Status label with Portal-style formatting
        self.status_label = tk.Label(
            self.status_frame,
            text="SELECT AN ACTION ABOVE, THEN SCAN A BARCODE",
            font=Theme.get_status_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_SECONDARY,
            wraplength=Theme.TEXT_WRAP_LENGTH
        )
        self.status_label.pack(pady=(Theme.STATUS_PADDING, 5))
        
        # Container for image and info side by side for compact layout
        product_info_container = tk.Frame(self.status_frame, bg=Theme.BACKGROUND)
        product_info_container.pack(pady=5)
        
        # Product image label - smaller and on the left
        self.image_label = tk.Label(
            product_info_container,
            bg=Theme.BACKGROUND,
            text=""  # Empty text initially
        )
        self.image_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Product info label - on the right of image
        self.info_label = tk.Label(
            product_info_container,
            text="",
            font=Theme.get_info_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY,
            wraplength=400,  # Reduced wrap length for compact display
            justify=tk.LEFT,
            anchor='w'
        )
        self.info_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize keyboard - pack before bottom buttons so it appears above them
        self.keyboard = OnScreenKeyboard(main_frame, callback=self._perform_search)
        
        # Bottom buttons container (search and config on same line)
        bottom_buttons_frame = tk.Frame(main_frame, bg=Theme.BACKGROUND)
        bottom_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Search icon button (bottom left)
        search_icon_frame = tk.Frame(bottom_buttons_frame, bg=Theme.BACKGROUND)
        search_icon_frame.pack(side=tk.LEFT, padx=10)
        
        search_icon_bg = tk.Frame(search_icon_frame, bg=Theme.BUTTON_CONFIG)
        icon_loader = get_icon_loader()
        search_icon_img = icon_loader.load_icon('search', size=(24, 24), color='white')
        if search_icon_img:
            search_icon = tk.Label(
                search_icon_bg,
                image=search_icon_img,
                bg=Theme.BUTTON_CONFIG,
            )
            search_icon.image = search_icon_img  # Keep reference
        else:
            # Fallback to text if icon not available
            search_icon = tk.Label(
                search_icon_bg,
                text="SEARCH",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_CONFIG,
                fg='white',
            )
        search_icon.pack(padx=8, pady=5)
        search_icon_bg.pack()
        
        # Bind click events - navigate to search page
        search_icon.bind('<Button-1>', lambda e: self._show_search_page())
        search_icon_bg.bind('<Button-1>', lambda e: self._show_search_page())
        
        # Hover effect for search button
        def search_enter(e): 
            search_icon_bg.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
            search_icon.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
        def search_leave(e): 
            search_icon_bg.config(bg=Theme.BUTTON_CONFIG)
            search_icon.config(bg=Theme.BUTTON_CONFIG)
        search_icon.bind('<Enter>', search_enter)
        search_icon.bind('<Leave>', search_leave)
        search_icon_bg.bind('<Enter>', search_enter)
        search_icon_bg.bind('<Leave>', search_leave)
        
        # Config button (bottom right) - icon only, no text
        config_button_frame = tk.Frame(bottom_buttons_frame, bg=Theme.BACKGROUND)
        config_button_frame.pack(side=tk.RIGHT, padx=10)
        
        config_bg_frame = tk.Frame(config_button_frame, bg=Theme.BUTTON_CONFIG)
        icon_loader = get_icon_loader()
        settings_icon_img = icon_loader.load_icon('settings', size=(24, 24), color='white')
        if settings_icon_img:
            config_button = tk.Label(
                config_bg_frame,
                image=settings_icon_img,
                bg=Theme.BUTTON_CONFIG,
            )
            config_button.image = settings_icon_img  # Keep reference
        else:
            # Fallback to text if icon not available
            config_button = tk.Label(
                config_bg_frame,
                text="CONFIG",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_CONFIG,
                fg='white',
            )
        config_button.pack(padx=8, pady=5)
        config_bg_frame.pack()
        
        # Bind click events
        config_button.bind('<Button-1>', lambda e: self._setup_config_page())
        config_bg_frame.bind('<Button-1>', lambda e: self._setup_config_page())
        
        # Hover effect for config button
        def config_enter(e): 
            config_bg_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#666666'))
            config_button.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#666666'))
        def config_leave(e): 
            config_bg_frame.config(bg=Theme.BUTTON_CONFIG)
            config_button.config(bg=Theme.BUTTON_CONFIG)
        config_button.bind('<Enter>', config_enter)
        config_button.bind('<Leave>', config_leave)
        config_bg_frame.bind('<Enter>', config_enter)
        config_bg_frame.bind('<Leave>', config_leave)
    
    def set_action(self, action: str):
        """Set the current action (add, open, or deduct). Toggle off if already selected."""
        # If clicking the same action that's already active, deselect it
        if self.current_action == action:
            self.current_action = None
            
            # Reset all buttons and indicators
            self.add_bg_frame.config(bg=Theme.BUTTON_ADD)
            self.add_button.config(bg=Theme.BUTTON_ADD)
            self.open_bg_frame.config(bg=Theme.BUTTON_OPEN)
            self.open_button.config(bg=Theme.BUTTON_OPEN)
            self.deduct_bg_frame.config(bg=Theme.BUTTON_DEDUCT)
            self.deduct_button.config(bg=Theme.BUTTON_DEDUCT)
            
            # Hide all indicators
            self.add_indicator.pack_forget()
            self.open_indicator.pack_forget()
            self.deduct_indicator.pack_forget()
            
            # Reset status message
            self.status_label.config(text="SELECT AN ACTION ABOVE, THEN SCAN A BARCODE", fg=Theme.TEXT_SECONDARY, font=Theme.get_status_font())
            
            # Clear previous results
            self.image_label.config(image='')
            self.info_label.config(text="")
            return
        
        # Set new action
        self.current_action = action
        
        # Reset all buttons and indicators - Update both label and frame
        self.add_bg_frame.config(bg=Theme.BUTTON_ADD)
        self.add_button.config(bg=Theme.BUTTON_ADD)
        self.open_bg_frame.config(bg=Theme.BUTTON_OPEN)
        self.open_button.config(bg=Theme.BUTTON_OPEN)
        self.deduct_bg_frame.config(bg=Theme.BUTTON_DEDUCT)
        self.deduct_button.config(bg=Theme.BUTTON_DEDUCT)
        
        # Hide all indicators
        self.add_indicator.pack_forget()
        self.open_indicator.pack_forget()
        self.deduct_indicator.pack_forget()
        
        # Set active button with visual indicator
        if action == 'add':
            self.add_bg_frame.config(bg=Theme.BUTTON_ADD_ACTIVE)
            self.add_button.config(bg=Theme.BUTTON_ADD_ACTIVE)
            # Show active indicator - pack at the top of button_frame
            self.add_indicator.pack(fill=tk.X, pady=(0, 2), before=self.add_bg_frame)
            self.status_label.config(text="READY TO ADD STOCK. SCAN A BARCODE...", fg=Theme.STATUS_SUCCESS)
        elif action == 'open':
            self.open_bg_frame.config(bg=Theme.BUTTON_OPEN_ACTIVE)
            self.open_button.config(bg=Theme.BUTTON_OPEN_ACTIVE)
            # Show active indicator - pack at the top of button_frame
            self.open_indicator.pack(fill=tk.X, pady=(0, 2), before=self.open_bg_frame)
            self.status_label.config(text="READY TO OPEN PRODUCT. SCAN A BARCODE...", fg=Theme.STATUS_WARNING)
        else:  # deduct
            self.deduct_bg_frame.config(bg=Theme.BUTTON_DEDUCT_ACTIVE)
            self.deduct_button.config(bg=Theme.BUTTON_DEDUCT_ACTIVE)
            # Show active indicator - pack at the top of button_frame
            self.deduct_indicator.pack(fill=tk.X, pady=(0, 2), before=self.deduct_bg_frame)
            self.status_label.config(text="READY TO DEDUCT STOCK. SCAN A BARCODE...", fg=Theme.STATUS_ERROR)
        
        # Clear previous results
        self.image_label.config(image='')
        self.info_label.config(text="")
    
    def _setup_config_page(self):
        """Setup the configuration page as a full view."""
        # Hide main page widgets
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()
        
        # Create config page frame
        self.config_page_frame = tk.Frame(self.main_frame, bg=Theme.BACKGROUND)
        self.config_page_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.config_page_frame, bg=Theme.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # Back button
        back_frame = tk.Frame(header_frame, bg=Theme.BUTTON_CONFIG)
        icon_loader = get_icon_loader()
        back_icon_img = icon_loader.load_icon('arrow_left', size=(20, 20), color='white')
        if back_icon_img:
            back_icon_label = tk.Label(
                back_frame,
                image=back_icon_img,
                bg=Theme.BUTTON_CONFIG,
            )
            back_icon_label.image = back_icon_img  # Keep reference
            back_icon_label.pack(side=tk.LEFT, padx=(10, 5), pady=8)
        back_label = tk.Label(
            back_frame,
            text="BACK",
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
        )
        back_label.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        back_frame.pack(side=tk.LEFT)
        back_label.bind('<Button-1>', lambda e: self._setup_main_page())
        back_frame.bind('<Button-1>', lambda e: self._setup_main_page())
        if back_icon_img:
            back_icon_label.bind('<Button-1>', lambda e: self._setup_main_page())
        
        # Hover effect for back button
        def back_enter(e): 
            back_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#666666'))
            back_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#666666'))
        def back_leave(e): 
            back_frame.config(bg=Theme.BUTTON_CONFIG)
            back_label.config(bg=Theme.BUTTON_CONFIG)
        back_label.bind('<Enter>', back_enter)
        back_label.bind('<Leave>', back_leave)
        back_frame.bind('<Enter>', back_enter)
        back_frame.bind('<Leave>', back_leave)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="CONFIGURATION",
            font=Theme.get_title_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Content frame (scrollable if needed)
        content_frame = tk.Frame(self.config_page_frame, bg=Theme.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Create keyboard for config page
        config_keyboard = OnScreenKeyboard(self.config_page_frame)
        
        # Host entry section
        host_label = tk.Label(
            content_frame,
            text="Grocy Host (e.g., https://grocy.example.com):",
            font=Theme.get_config_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        host_label.pack(pady=(0, 10), anchor='w')
        
        host_entry_frame = tk.Frame(content_frame, bg=Theme.BACKGROUND)
        host_entry_frame.pack(fill=tk.X, pady=(0, 20))
        
        host_entry = tk.Entry(
            host_entry_frame, 
            font=Theme.get_config_font(), 
            bg=Theme.BUTTON_CONFIG, 
            fg='white', 
            insertbackground='white'
        )
        host_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if self.config.host:
            host_entry.insert(0, self.config.host)
        
        # Keyboard button for host entry
        icon_loader = get_icon_loader()
        keyboard_icon_img = icon_loader.load_icon('keyboard', size=(24, 24), color='white')
        if keyboard_icon_img:
            host_keyboard_btn = tk.Label(
                host_entry_frame,
                image=keyboard_icon_img,
                bg=Theme.BUTTON_ADD,
            )
            host_keyboard_btn.image = keyboard_icon_img  # Keep reference
        else:
            host_keyboard_btn = tk.Label(
                host_entry_frame,
                text="KB",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_ADD,
                fg='white',
            )
        host_keyboard_btn.pack(side=tk.LEFT, padx=10)
        host_keyboard_btn.bind('<Button-1>', lambda e: config_keyboard.show(host_entry))
        
        # API key entry section
        api_key_label = tk.Label(
            content_frame,
            text="API Key:",
            font=Theme.get_config_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        api_key_label.pack(pady=(0, 10), anchor='w')
        
        api_key_entry_frame = tk.Frame(content_frame, bg=Theme.BACKGROUND)
        api_key_entry_frame.pack(fill=tk.X, pady=(0, 30))
        
        api_key_entry = tk.Entry(
            api_key_entry_frame, 
            font=Theme.get_config_font(), 
            show='*',
            bg=Theme.BUTTON_CONFIG, 
            fg='white', 
            insertbackground='white'
        )
        api_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if self.config.api_key:
            api_key_entry.insert(0, self.config.api_key)
        
        # Keyboard button for API key entry
        icon_loader = get_icon_loader()
        keyboard_icon_img = icon_loader.load_icon('keyboard', size=(24, 24), color='white')
        if keyboard_icon_img:
            api_keyboard_btn = tk.Label(
                api_key_entry_frame,
                image=keyboard_icon_img,
                bg=Theme.BUTTON_ADD,
            )
            api_keyboard_btn.image = keyboard_icon_img  # Keep reference
        else:
            api_keyboard_btn = tk.Label(
                api_key_entry_frame,
                text="KB",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_ADD,
                fg='white',
            )
        api_keyboard_btn.pack(side=tk.LEFT, padx=10)
        api_keyboard_btn.bind('<Button-1>', lambda e: config_keyboard.show(api_key_entry))
        
        # Status label for feedback
        status_label = tk.Label(
            content_frame,
            text="",
            font=Theme.get_config_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.STATUS_SUCCESS
        )
        status_label.pack(pady=10)
        
        def save_config():
            host = host_entry.get().strip()
            api_key = api_key_entry.get().strip()
            
            if not host or not api_key:
                status_label.config(text="Please fill in all fields.", fg=Theme.STATUS_ERROR)
                return
            
            if self.config.save(host, api_key):
                self.grocy_api = GrocyAPI(self.config)
                if self.grocy_api.test_connection():
                    status_label.config(text="SUCCESS: Configuration saved and connection tested!", fg=Theme.STATUS_SUCCESS)
                    # Return to main page after a short delay
                    self.root.after(1500, self._setup_main_page)
                else:
                    status_label.config(text="ERROR: Could not connect to Grocy. Please check your settings.", fg=Theme.STATUS_ERROR)
            else:
                status_label.config(text="ERROR: Failed to save configuration.", fg=Theme.STATUS_ERROR)
        
        # Save button
        save_button_frame = tk.Frame(content_frame, bg=Theme.BACKGROUND)
        save_button_frame.pack(pady=20)
        
        save_bg_frame = tk.Frame(save_button_frame, bg=Theme.BUTTON_SAVE)
        save_button = tk.Label(
            save_bg_frame,
            text="SAVE CONFIGURATION",
            font=Theme.get_config_button_font(),
            bg=Theme.BUTTON_SAVE,
            fg='white',
        )
        save_button.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        save_bg_frame.pack()
        
        # Bind click events
        save_button.bind('<Button-1>', lambda e: save_config())
        save_bg_frame.bind('<Button-1>', lambda e: save_config())
        
        # Hover effect
        def save_enter(e): 
            save_bg_frame.config(bg=getattr(Theme, 'BUTTON_SAVE_HOVER', Theme.BUTTON_ADD_HOVER))
            save_button.config(bg=getattr(Theme, 'BUTTON_SAVE_HOVER', Theme.BUTTON_ADD_HOVER))
        def save_leave(e): 
            save_bg_frame.config(bg=Theme.BUTTON_SAVE)
            save_button.config(bg=Theme.BUTTON_SAVE)
        save_button.bind('<Enter>', save_enter)
        save_button.bind('<Leave>', save_leave)
        save_bg_frame.bind('<Enter>', save_enter)
        save_bg_frame.bind('<Leave>', save_leave)
    
    def process_barcode(self, barcode: str):
        """Process a scanned barcode."""
        if not self.grocy_api:
            self.status_label.config(text="GROCY NOT CONFIGURED!", fg=Theme.STATUS_ERROR)
            return
        
        # If no action is selected, open product detail page instead
        if not self.current_action:
            # Show scanning status
            self.status_label.config(text=f"LOOKING UP PRODUCT: {barcode}...", fg=Theme.STATUS_WARNING)
            self.root.update()
            
            # Look up product and show detail page
            threading.Thread(target=self._lookup_product_and_show_detail, args=(barcode,), daemon=True).start()
            return
        
        # Show scanning status
        self.status_label.config(text=f"PROCESSING BARCODE: {barcode}...", fg=Theme.STATUS_WARNING)
        self.root.update()
        
        # Process in thread to avoid blocking UI
        threading.Thread(target=self._process_barcode_thread, args=(barcode,), daemon=True).start()
    
    def _lookup_product_and_show_detail(self, barcode: str):
        """Look up product by barcode and show detail page."""
        try:
            # Get product by barcode
            product = self.grocy_api.get_product_by_barcode(barcode)
            
            if not product:
                self.root.after(0, self._show_error, f"Barcode '{barcode}' not found in Grocy")
                return
            
            product_id = product['id']
            
            # Show product detail page
            self.root.after(0, self._show_product_detail, product_id)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error: {str(e)}")
    
    def _process_barcode_thread(self, barcode: str):
        """Process barcode in background thread."""
        try:
            # Get product by barcode
            product = self.grocy_api.get_product_by_barcode(barcode)
            
            if not product:
                self.root.after(0, self._show_error, f"Barcode '{barcode}' not found in Grocy")
                return
            
            product_id = product['id']
            product_name = product.get('name', 'Unknown Product')
            
            # Perform action
            if self.current_action == 'add':
                result = self.grocy_api.add_to_stock(product_id, amount=1.0)
            elif self.current_action == 'open':
                result = self.grocy_api.open_product(product_id, amount=1.0)
            else:  # deduct
                result = self.grocy_api.deduct_from_stock(product_id, amount=1.0)
            
            if not result:
                self.root.after(0, self._show_error, "Failed to update stock")
                return
            
            # Get updated stock - wait a moment for API to update
            import time
            time.sleep(0.5)  # Longer delay to ensure stock is updated
            
            # Try multiple times to get updated stock
            stock_amount = 0
            for attempt in range(3):
                stock = self.grocy_api.get_stock(product_id)
                # Stock can be returned as a list or dict depending on Grocy version
                if isinstance(stock, list) and len(stock) > 0:
                    # If it's a list, sum all stock entries
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                    if stock_amount > 0:
                        break
                elif isinstance(stock, dict):
                    # If it's a dict, get amount directly
                    stock_amount = stock.get('amount', 0)
                    if stock_amount > 0:
                        break
                    # Also try 'stock_amount' key
                    stock_amount = stock.get('stock_amount', stock_amount)
                    if stock_amount > 0:
                        break
                
                if attempt < 2:
                    time.sleep(0.3)  # Wait a bit more before retry
            
            print(f"  Final stock amount: {stock_amount}")
            
            # Get product picture - try multiple sources
            picture_file_name = product.get('picture_file_name')
            image_url = None
            
            if picture_file_name:
                image_url = self.grocy_api.get_product_picture_url(product_id, picture_file_name)
                print(f"  Product image URL: {image_url}")
            else:
                # Try to get product again to see if picture_file_name is there
                print(f"  No picture_file_name in product, trying to fetch product again...")
                updated_product = self.grocy_api.get_product_by_id(product_id)
                if updated_product:
                    picture_file_name = updated_product.get('picture_file_name')
                    if picture_file_name:
                        image_url = self.grocy_api.get_product_picture_url(product_id, picture_file_name)
                        print(f"  Found picture_file_name on second try: {picture_file_name}")
            
            # Show success
            self.root.after(0, self._show_success, product_name, image_url, stock_amount, product_id)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error: {str(e)}")
    
    def _show_success(self, product_name: str, image_url: Optional[str], stock_amount: float, product_id: Optional[int] = None):
        """Show success message with product info."""
        self.status_label.config(text="SUCCESS", fg=Theme.STATUS_SUCCESS, font=Theme.get_status_large_font())
        self.info_label.config(
            text=f"PRODUCT: {product_name.upper()}\nNEW STOCK: {stock_amount}",
            fg=Theme.STATUS_SUCCESS,
            font=Theme.get_info_font()
        )
        
        # Load and display product image (supports transparent PNG)
        if image_url or product_id:
            # Extract picture_file_name from URL if available
            picture_file_name = None
            if image_url:
                # Extract filename from URL (remove query params if any)
                picture_file_name = image_url.split('/')[-1].split('?')[0]
            
            # Try multiple URL formats if the first one fails
            base_url = self.grocy_api.base_url
            
            urls_to_try = []
            if image_url:
                urls_to_try.append(image_url)  # Original URL
            
            # Use helper function to build Grocy image URLs (with base64 encoding)
            if picture_file_name:
                urls_to_try.extend(build_grocy_image_urls(
                    base_url, 
                    picture_file_name, 
                    product_id, 
                    self.grocy_api.api_key
                ))
            
            img_loaded = False
            for url in urls_to_try:
                try:
                    print(f"  Trying image URL: {url}")
                    response = requests.get(url, timeout=5, headers={'GROCY-API-KEY': self.grocy_api.api_key})
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        
                        # Handle transparent PNGs by compositing on dark background
                        if img.mode == 'RGBA':
                            # Create a dark background matching the UI theme
                            # Convert hex color to RGB tuple
                            bg_color = tuple(int(Theme.BACKGROUND[i:i+2], 16) for i in (1, 3, 5))
                            background = Image.new('RGB', img.size, bg_color)
                            # Paste the RGBA image on the background using alpha channel as mask
                            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize while maintaining aspect ratio
                        img.thumbnail(Theme.PRODUCT_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        
                        # Convert to PhotoImage for tkinter
                        photo = ImageTk.PhotoImage(img)
                        self.image_label.config(image=photo, bg=Theme.BACKGROUND)
                        self.image_label.image = photo  # Keep a reference
                        print(f"  ✓ Image loaded and displayed ({img.size[0]}x{img.size[1]}) from: {url}")
                        img_loaded = True
                        break
                    else:
                        print(f"  ✗ URL returned status {response.status_code}")
                except Exception as e:
                    print(f"  ✗ Error with URL {url}: {e}")
                    continue
            
            if not img_loaded:
                print(f"  ✗ Could not load image from any URL")
                print(f"    Tried {len(urls_to_try)} different URL formats")
        else:
            print(f"  No image URL or product_id available")
        
        # Reset action after delay
        self.root.after(Theme.STATUS_RESET_DELAY, self._reset_status)
    
    def _toggle_search(self):
        """Toggle search bar visibility."""
        if self.search_frame.winfo_viewable():
            self.search_frame.pack_forget()
            self.keyboard.hide()
        else:
            self.search_frame.pack(fill=tk.X, pady=5, before=self.status_frame)
            self.search_entry.delete(0, tk.END)
            self.search_entry.focus_set()
            self.keyboard.show(self.search_entry)
    
    def _perform_search(self):
        """Perform product search."""
        if not self.grocy_api:
            self.status_label.config(text="GROCY NOT CONFIGURED!", fg=Theme.STATUS_ERROR)
            return
        
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
        
        # Hide search and keyboard
        self.search_frame.pack_forget()
        self.keyboard.hide()
        
        # Show searching status
        self.status_label.config(text=f"SEARCHING: {search_term.upper()}...", fg=Theme.STATUS_WARNING)
        self.root.update()
        
        # Search in background thread
        threading.Thread(target=self._search_thread, args=(search_term,), daemon=True).start()
    
    def _search_thread(self, search_term: str):
        """Search for products in background thread."""
        try:
            # Search products by name
            products = self.grocy_api.search_products(search_term)
            
            if products and len(products) > 0:
                # Show first matching product
                product = products[0]
                product_id = product['id']
                product_name = product.get('name', 'Unknown Product')
                
                # Get stock
                import time
                time.sleep(0.2)
                stock = self.grocy_api.get_stock(product_id)
                if isinstance(stock, list) and len(stock) > 0:
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                elif isinstance(stock, dict):
                    stock_amount = stock.get('amount', 0)
                else:
                    stock_amount = 0
                
                # Get image
                picture_file_name = product.get('picture_file_name')
                image_url = None
                if picture_file_name:
                    image_url = self.grocy_api.get_product_picture_url(product_id, picture_file_name)
                
                # Show result
                self.root.after(0, self._show_search_result, product_name, image_url, stock_amount, product_id)
            else:
                self.root.after(0, self._show_error, f"No products found matching '{search_term}'")
                
        except Exception as e:
            self.root.after(0, self._show_error, f"Search error: {str(e)}")
    
    def _show_search_result(self, product_name: str, image_url: Optional[str], stock_amount: float, product_id: int):
        """Show search result."""
        self.status_label.config(text="PRODUCT FOUND", fg=Theme.STATUS_SUCCESS, font=Theme.get_status_large_font())
        self.info_label.config(
            text=f"PRODUCT: {product_name.upper()}\nSTOCK: {stock_amount}",
            fg=Theme.STATUS_SUCCESS,
            font=Theme.get_info_font()
        )
        
        # Load and display product image (reuse same logic as _show_success)
        if image_url or product_id:
            # Extract picture_file_name from URL if available
            picture_file_name = None
            if image_url:
                picture_file_name = image_url.split('/')[-1].split('?')[0]
            
            base_url = self.grocy_api.base_url
            urls_to_try = []
            if image_url:
                urls_to_try.append(image_url)
            
            # Use helper function to build Grocy image URLs (with base64 encoding)
            if picture_file_name:
                urls_to_try.extend(build_grocy_image_urls(
                    base_url, 
                    picture_file_name, 
                    product_id, 
                    self.grocy_api.api_key
                ))
            
            img_loaded = False
            for url in urls_to_try:
                try:
                    response = requests.get(url, timeout=5, headers={'GROCY-API-KEY': self.grocy_api.api_key})
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        
                        if img.mode == 'RGBA':
                            bg_color = tuple(int(Theme.BACKGROUND[i:i+2], 16) for i in (1, 3, 5))
                            background = Image.new('RGB', img.size, bg_color)
                            background.paste(img, mask=img.split()[3])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        img.thumbnail(Theme.PRODUCT_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.image_label.config(image=photo, bg=Theme.BACKGROUND)
                        self.image_label.image = photo
                        img_loaded = True
                        break
                except:
                    continue
        
        # Reset after delay
        self.root.after(Theme.STATUS_RESET_DELAY, self._reset_status)
    
    def _show_error(self, message: str):
        """Show error message."""
        self.status_label.config(text="FAILED", fg=Theme.STATUS_ERROR, font=Theme.get_status_large_font())
        self.info_label.config(text=message.upper(), fg=Theme.STATUS_ERROR, font=Theme.get_info_font())
        self.image_label.config(image='')
        
        # Reset action after delay
        self.root.after(Theme.STATUS_RESET_DELAY, self._reset_status)
    
    def _reset_status(self):
        """Reset status display."""
        if self.current_action == 'add':
            self.status_label.config(text="READY TO ADD STOCK. SCAN A BARCODE...", fg=Theme.STATUS_SUCCESS, font=Theme.get_status_font())
        elif self.current_action == 'open':
            self.status_label.config(text="READY TO OPEN PRODUCT. SCAN A BARCODE...", fg=Theme.STATUS_WARNING, font=Theme.get_status_font())
        elif self.current_action == 'deduct':
            self.status_label.config(text="READY TO DEDUCT STOCK. SCAN A BARCODE...", fg=Theme.STATUS_ERROR, font=Theme.get_status_font())
        else:
            self.status_label.config(text="SELECT AN ACTION ABOVE, THEN SCAN A BARCODE", fg=Theme.TEXT_SECONDARY, font=Theme.get_status_font())
        self.info_label.config(text="")
        self.image_label.config(image='')
    
    def _toggle_search(self):
        """Toggle search bar visibility."""
        if self.search_frame.winfo_viewable():
            self.search_frame.pack_forget()
            self.keyboard.hide()
        else:
            self.search_frame.pack(fill=tk.X, pady=5, before=self.status_frame)
            self.search_entry.delete(0, tk.END)
            self.search_entry.focus_set()
            self.keyboard.show(self.search_entry)
    
    def _perform_search(self):
        """Perform product search."""
        if not self.grocy_api:
            self.status_label.config(text="GROCY NOT CONFIGURED!", fg=Theme.STATUS_ERROR)
            return
        
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
        
        # Hide search and keyboard
        self.search_frame.pack_forget()
        self.keyboard.hide()
        
        # Show searching status
        self.status_label.config(text=f"SEARCHING: {search_term.upper()}...", fg=Theme.STATUS_WARNING)
        self.root.update()
        
        # Search in background thread
        threading.Thread(target=self._search_thread, args=(search_term,), daemon=True).start()
    
    def _search_thread(self, search_term: str):
        """Search for products in background thread."""
        try:
            # Search products by name
            products = self.grocy_api.search_products(search_term)
            
            if products and len(products) > 0:
                # Show first matching product
                product = products[0]
                product_id = product['id']
                product_name = product.get('name', 'Unknown Product')
                
                # Get stock
                import time
                time.sleep(0.2)
                stock = self.grocy_api.get_stock(product_id)
                if isinstance(stock, list) and len(stock) > 0:
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                elif isinstance(stock, dict):
                    stock_amount = stock.get('amount', 0)
                else:
                    stock_amount = 0
                
                # Get image
                picture_file_name = product.get('picture_file_name')
                image_url = None
                if picture_file_name:
                    image_url = self.grocy_api.get_product_picture_url(product_id, picture_file_name)
                
                # Show result
                self.root.after(0, self._show_search_result, product_name, image_url, stock_amount, product_id)
            else:
                self.root.after(0, self._show_error, f"No products found matching '{search_term}'")
                
        except Exception as e:
            self.root.after(0, self._show_error, f"Search error: {str(e)}")
    
    def _show_search_result(self, product_name: str, image_url: Optional[str], stock_amount: float, product_id: int):
        """Show search result."""
        self.status_label.config(text="PRODUCT FOUND", fg=Theme.STATUS_SUCCESS, font=Theme.get_status_large_font())
        self.info_label.config(
            text=f"PRODUCT: {product_name.upper()}\nSTOCK: {stock_amount}",
            fg=Theme.STATUS_SUCCESS,
            font=Theme.get_info_font()
        )
        
        # Load and display product image
        if image_url or product_id:
            # Extract picture_file_name from URL if available
            picture_file_name = None
            if image_url:
                picture_file_name = image_url.split('/')[-1].split('?')[0]
            
            base_url = self.grocy_api.base_url
            urls_to_try = []
            if image_url:
                urls_to_try.append(image_url)
            
            # Use helper function to build Grocy image URLs (with base64 encoding)
            if picture_file_name:
                urls_to_try.extend(build_grocy_image_urls(
                    base_url, 
                    picture_file_name, 
                    product_id, 
                    self.grocy_api.api_key
                ))
            
            img_loaded = False
            for url in urls_to_try:
                try:
                    response = requests.get(url, timeout=5, headers={'GROCY-API-KEY': self.grocy_api.api_key})
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        
                        if img.mode == 'RGBA':
                            bg_color = tuple(int(Theme.BACKGROUND[i:i+2], 16) for i in (1, 3, 5))
                            background = Image.new('RGB', img.size, bg_color)
                            background.paste(img, mask=img.split()[3])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        img.thumbnail(Theme.PRODUCT_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.image_label.config(image=photo, bg=Theme.BACKGROUND)
                        self.image_label.image = photo
                        img_loaded = True
                        break
                except:
                    continue
        
        # Reset after delay
        self.root.after(Theme.STATUS_RESET_DELAY, self._reset_status)


    def _show_search_page(self):
        """Navigate to search page."""
        self._clear_pages()
        self.current_page = 'search'
        self._setup_search_page()
    
    def _setup_search_page(self):
        """Setup the search page with scrollable product list."""
        # Hide main page widgets
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()
        
        # Create search page frame
        self.search_page_frame = tk.Frame(self.main_frame, bg=Theme.BACKGROUND)
        self.search_page_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.search_page_frame, bg=Theme.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Back button
        back_frame = tk.Frame(header_frame, bg=Theme.BUTTON_CONFIG)
        icon_loader = get_icon_loader()
        back_icon_img = icon_loader.load_icon('arrow_left', size=(18, 18), color='white')
        if back_icon_img:
            back_icon_label = tk.Label(
                back_frame,
                image=back_icon_img,
                bg=Theme.BUTTON_CONFIG,
            )
            back_icon_label.image = back_icon_img  # Keep reference
            back_icon_label.pack(side=tk.LEFT, padx=(8, 3), pady=5)
        back_label = tk.Label(
            back_frame,
            text="BACK",
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
        )
        back_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        back_frame.pack(side=tk.LEFT)
        back_label.bind('<Button-1>', lambda e: self._setup_main_page())
        back_frame.bind('<Button-1>', lambda e: self._setup_main_page())
        if back_icon_img:
            back_icon_label.bind('<Button-1>', lambda e: self._setup_main_page())
        
        # Hover effect for back button
        def back_enter(e): back_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')); back_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')); (back_icon_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')) if back_icon_img else None)
        def back_leave(e): back_frame.config(bg=Theme.BUTTON_CONFIG); back_label.config(bg=Theme.BUTTON_CONFIG); (back_icon_label.config(bg=Theme.BUTTON_CONFIG) if back_icon_img else None)
        back_label.bind('<Enter>', back_enter)
        back_label.bind('<Leave>', back_leave)
        back_frame.bind('<Enter>', back_enter)
        back_frame.bind('<Leave>', back_leave)
        if back_icon_img:
            back_icon_label.bind('<Enter>', back_enter)
            back_icon_label.bind('<Leave>', back_leave)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="SEARCH PRODUCTS",
            font=Theme.get_title_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Search input frame
        search_input_frame = tk.Frame(self.search_page_frame, bg=Theme.BACKGROUND)
        search_input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.search_entry = tk.Entry(
            search_input_frame,
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
            insertbackground='white',
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
        
        # Search button
        search_button_frame = tk.Frame(search_input_frame, bg=Theme.BUTTON_ADD)
        search_button = tk.Label(
            search_button_frame,
            text="🔍 SEARCH",
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_ADD,
            fg='white',
        )
        search_button.pack(padx=10, pady=5)
        search_button_frame.pack(side=tk.LEFT, padx=5)
        search_button.bind('<Button-1>', lambda e: self._perform_search())
        search_button_frame.bind('<Button-1>', lambda e: self._perform_search())
        
        # Hover effect
        def search_btn_enter(e): search_button_frame.config(bg=Theme.BUTTON_ADD_HOVER); search_button.config(bg=Theme.BUTTON_ADD_HOVER)
        def search_btn_leave(e): search_button_frame.config(bg=Theme.BUTTON_ADD); search_button.config(bg=Theme.BUTTON_ADD)
        search_button.bind('<Enter>', search_btn_enter)
        search_button.bind('<Leave>', search_btn_leave)
        search_button_frame.bind('<Enter>', search_btn_enter)
        search_button_frame.bind('<Leave>', search_btn_leave)
        
        # Initialize keyboard for search with callback for Enter key
        if not hasattr(self, 'keyboard') or self.keyboard is None:
            self.keyboard = OnScreenKeyboard(self.search_page_frame, target_entry=self.search_entry, callback=self._perform_search)
        
        # Keyboard toggle button
        keyboard_frame = tk.Frame(search_input_frame, bg=Theme.BUTTON_CONFIG)
        keyboard_button = tk.Label(
            keyboard_frame,
            text="⌨",
            font=('Arial', 16),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
        )
        keyboard_button.pack(padx=8, pady=5)
        keyboard_frame.pack(side=tk.LEFT, padx=5)
        keyboard_button.bind('<Button-1>', lambda e: self._toggle_keyboard())
        keyboard_frame.bind('<Button-1>', lambda e: self._toggle_keyboard())
        
        # Filter frame: Hide/Show out-of-stock products + Product group filters
        filter_frame = tk.Frame(self.search_page_frame, bg=Theme.BACKGROUND)
        filter_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Left side: Toggle button for hiding out-of-stock products
        filter_left_frame = tk.Frame(filter_frame, bg=Theme.BACKGROUND)
        filter_left_frame.pack(side=tk.LEFT)
        
        self.hide_out_of_stock = False
        self.selected_product_group = None
        toggle_frame = tk.Frame(filter_left_frame, bg=Theme.BUTTON_CONFIG)
        toggle_label = tk.Label(
            toggle_frame,
            text="🔲 Hide out-of-stock",
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
        )
        toggle_label.pack(padx=10, pady=5)
        toggle_frame.pack(side=tk.LEFT, padx=5)
        toggle_label.bind('<Button-1>', lambda e: self._toggle_out_of_stock_filter())
        toggle_frame.bind('<Button-1>', lambda e: self._toggle_out_of_stock_filter())
        
        # Hover effect for toggle
        def toggle_enter(e): toggle_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')); toggle_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
        def toggle_leave(e): toggle_frame.config(bg=Theme.BUTTON_CONFIG); toggle_label.config(bg=Theme.BUTTON_CONFIG)
        toggle_label.bind('<Enter>', toggle_enter)
        toggle_label.bind('<Leave>', toggle_leave)
        toggle_frame.bind('<Enter>', toggle_enter)
        toggle_frame.bind('<Leave>', toggle_leave)
        
        self.filter_toggle_label = toggle_label  # Store reference for updating text
        
        # Right side: Product group filter buttons
        filter_right_frame = tk.Frame(filter_frame, bg=Theme.BACKGROUND)
        filter_right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Label for product groups
        groups_label = tk.Label(
            filter_right_frame,
            text="Groups:",
            font=Theme.get_config_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_SECONDARY
        )
        groups_label.pack(side=tk.LEFT, padx=5)
        
        # Container for product group buttons (scrollable if needed)
        groups_container = tk.Frame(filter_right_frame, bg=Theme.BACKGROUND)
        groups_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.product_group_buttons = {}
        self.groups_container = groups_container  # Store reference
        
        # Load product groups in background thread
        if self.grocy_api:
            threading.Thread(target=self._load_product_groups, daemon=True).start()
        
        # Status label to show selected group
        self.group_indicator_label = tk.Label(
            self.search_page_frame,
            text="",
            font=Theme.get_config_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.STATUS_INFO,
            anchor='w'
        )
        self.group_indicator_label.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        # Load initial 10 products
        if self.grocy_api:
            threading.Thread(target=self._load_initial_products, daemon=True).start()
        
        # Results frame with scrollbar
        results_container = tk.Frame(self.search_page_frame, bg=Theme.BACKGROUND)
        results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas and scrollbar for scrollable list
        canvas = tk.Canvas(results_container, bg=Theme.BACKGROUND, highlightthickness=0)
        scrollbar = tk.Scrollbar(results_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.BACKGROUND)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Touch scrolling support
        self._setup_touch_scrolling(canvas, scrollable_frame)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Hide scrollbar for touch interface (can be re-enabled if needed)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store references
        self.search_results_frame = scrollable_frame
        self.search_canvas = canvas
        self.search_scrollbar = scrollbar
        self.search_results_grid_cols = 3  # Number of columns in grid
        
        # Status label
        self.search_status_label = tk.Label(
            self.search_page_frame,
            text="Enter search term and press Search",
            font=Theme.get_status_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_SECONDARY
        )
        self.search_status_label.pack(pady=10)
    
    def _setup_touch_scrolling(self, canvas: tk.Canvas, scrollable_frame: tk.Frame):
        """
        Setup touch scrolling for canvas.
        Supports drag-to-scroll (swipe gestures) for touch interfaces.
        """
        # Variables to track scrolling
        self._scroll_start_y = 0
        self._scroll_start_pos = 0
        self._is_scrolling = False
        
        def on_touch_start(event):
            """Handle touch/mouse press - start scrolling."""
            # Only start scrolling if clicking on canvas background, not on widgets
            if event.widget == canvas or event.widget == scrollable_frame:
                self._scroll_start_y = event.y
                self._scroll_start_pos = canvas.canvasy(0)
                self._is_scrolling = True
                canvas.scan_mark(event.x, event.y)
                return "break"  # Prevent event propagation
        
        def on_touch_move(event):
            """Handle touch/mouse drag - scroll canvas."""
            if self._is_scrolling:
                # Scroll the canvas smoothly
                canvas.scan_dragto(event.x, event.y, gain=1)
                # Update scroll region
                canvas.configure(scrollregion=canvas.bbox("all"))
                return "break"  # Prevent event propagation
        
        def on_touch_end(event):
            """Handle touch/mouse release - stop scrolling."""
            self._is_scrolling = False
        
        # Bind touch/mouse events for scrolling on canvas
        canvas.bind("<Button-1>", on_touch_start)
        canvas.bind("<B1-Motion>", on_touch_move)
        canvas.bind("<ButtonRelease-1>", on_touch_end)
        
        # Enable mouse wheel scrolling as fallback (for testing)
        def on_mousewheel(event):
            """Handle mouse wheel scrolling."""
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mouse wheel (works on some touchpads)
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Make canvas focusable for keyboard scrolling
        canvas.focus_set()
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.bind("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        canvas.bind("<Next>", lambda e: canvas.yview_scroll(1, "pages"))
        
        # Focus on search entry and show keyboard automatically
        self.search_entry.focus_set()
        # Show keyboard automatically when search page opens
        self.root.after(100, lambda: self.keyboard.show(self.search_entry))
    
    def _toggle_keyboard(self):
        """Toggle onscreen keyboard visibility."""
        if self.keyboard.is_visible():
            self.keyboard.hide()
        else:
            self.keyboard.show(self.search_entry)
    
    def _perform_search(self, search_value: Optional[str] = None):
        """Perform product search and show results.
        
        Args:
            search_value: Optional search value (if called from keyboard callback).
                         If None, reads from search_entry.
        """
        if not self.grocy_api:
            if hasattr(self, 'search_status_label'):
                self.search_status_label.config(text="GROCY NOT CONFIGURED!", fg=Theme.STATUS_ERROR)
            return
        
        # Get search term from parameter or entry field
        if search_value is not None:
            search_term = search_value.strip()
        else:
            search_term = self.search_entry.get().strip()
        
        if not search_term:
            return
        
        # Hide keyboard
        if self.keyboard:
            self.keyboard.hide()
        
        # Show searching status
        if hasattr(self, 'search_status_label'):
            self.search_status_label.config(text=f"SEARCHING: {search_term.upper()}...", fg=Theme.STATUS_WARNING)
        self.root.update()
        
        # Clear previous results
        if hasattr(self, 'search_results_frame'):
            for widget in self.search_results_frame.winfo_children():
                widget.destroy()
        
        # Search in background thread
        threading.Thread(target=self._search_thread_new, args=(search_term,), daemon=True).start()
    
    def _search_thread_new(self, search_term: str):
        """Search for products in background thread (new version for search page)."""
        try:
            products = self.grocy_api.search_products(search_term)
            
            if products and len(products) > 0:
                self.search_results = products
                self.root.after(0, self._display_search_results, products)
                # Update group indicator
                self.root.after(0, self._update_group_indicator)
            else:
                self.root.after(0, lambda: self.search_status_label.config(
                    text=f"No products found matching '{search_term}'",
                    fg=Theme.STATUS_ERROR
                ) if hasattr(self, 'search_status_label') else None)
        except Exception as e:
            self.root.after(0, lambda: self.search_status_label.config(
                text=f"Search error: {str(e)}",
                fg=Theme.STATUS_ERROR
            ) if hasattr(self, 'search_status_label') else None)
    
    def _load_product_groups(self):
        """Load product groups from Grocy API in background thread."""
        try:
            groups = self.grocy_api.get_product_groups()
            
            # Add "All" option first
            all_groups = [{'id': None, 'name': 'All'}] + groups
            
            # Update UI in main thread
            self.root.after(0, self._display_product_group_filters, all_groups)
        except Exception as e:
            print(f"Error loading product groups: {e}")
    
    def _load_initial_products(self):
        """Load initial 10 products when search page opens."""
        try:
            products = self.grocy_api.get_recent_products(limit=10)
            if products:
                self.root.after(0, self._display_search_results, products)
        except Exception as e:
            print(f"Error loading initial products: {e}")
    
    def _update_group_indicator(self):
        """Update the group indicator label to show selected group."""
        if hasattr(self, 'group_indicator_label'):
            if self.selected_product_group is None:
                self.group_indicator_label.config(text="Showing: All products", fg=Theme.STATUS_INFO)
            else:
                group_name = "Unknown"
                if self.selected_product_group in self.product_group_buttons:
                    group_name = self.product_group_buttons[self.selected_product_group].get('name', 'Unknown')
                self.group_indicator_label.config(text=f"Showing: {group_name}", fg=Theme.STATUS_SUCCESS)
    
    def _display_product_group_filters(self, groups: list):
        """Display product group filter buttons."""
        # Clear existing buttons
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        self.product_group_buttons = {}
        
        for group in groups:
            group_id = group.get('id')
            group_name = group.get('name', 'Unknown')
            
            # Create filter button
            group_frame = tk.Frame(self.groups_container, bg=Theme.BUTTON_CONFIG)
            group_label = tk.Label(
                group_frame,
                text=group_name,
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_CONFIG,
                fg='white',
            )
            group_label.pack(padx=8, pady=3)
            group_frame.pack(side=tk.LEFT, padx=3)
            
            # Store reference
            self.product_group_buttons[group_id] = {
                'frame': group_frame,
                'label': group_label,
                'name': group_name
            }
            
            # Bind click to filter by group
            def make_group_handler(gid):
                return lambda e: self._filter_by_product_group(gid)
            
            group_label.bind('<Button-1>', make_group_handler(group_id))
            group_frame.bind('<Button-1>', make_group_handler(group_id))
            
            # Hover effect
            def make_group_hover(frame, label):
                def enter(e): 
                    frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                def leave(e): 
                    frame.config(bg=Theme.BUTTON_CONFIG)
                    label.config(bg=Theme.BUTTON_CONFIG)
                return enter, leave
            
            enter_handler, leave_handler = make_group_hover(group_frame, group_label)
            group_label.bind('<Enter>', enter_handler)
            group_label.bind('<Leave>', leave_handler)
            group_frame.bind('<Enter>', enter_handler)
            group_frame.bind('<Leave>', leave_handler)
        
        # Highlight "All" by default
        if None in self.product_group_buttons:
            self._highlight_product_group_button(None)
        
        # Update group indicator
        self._update_group_indicator()
    
    def _filter_by_product_group(self, group_id: Optional[int]):
        """Filter products by selected product group."""
        self.selected_product_group = group_id
        
        # Update button highlights
        for gid, button_data in self.product_group_buttons.items():
            if gid == group_id:
                self._highlight_product_group_button(gid)
            else:
                self._unhighlight_product_group_button(gid)
        
        # Update group indicator
        self._update_group_indicator()
        
        # Re-display results with filter applied
        if hasattr(self, 'search_results') and self.search_results:
            self._display_search_results(self.search_results)
    
    def _highlight_product_group_button(self, group_id: Optional[int]):
        """Highlight a product group filter button."""
        if group_id in self.product_group_buttons:
            button_data = self.product_group_buttons[group_id]
            button_data['frame'].config(bg=Theme.BUTTON_ADD)
            button_data['label'].config(bg=Theme.BUTTON_ADD)
    
    def _unhighlight_product_group_button(self, group_id: Optional[int]):
        """Unhighlight a product group filter button."""
        if group_id in self.product_group_buttons:
            button_data = self.product_group_buttons[group_id]
            button_data['frame'].config(bg=Theme.BUTTON_CONFIG)
            button_data['label'].config(bg=Theme.BUTTON_CONFIG)
    
    def _toggle_out_of_stock_filter(self):
        """Toggle hide/show out-of-stock products filter."""
        self.hide_out_of_stock = not self.hide_out_of_stock
        
        # Update toggle button text
        if hasattr(self, 'filter_toggle_label'):
            if self.hide_out_of_stock:
                self.filter_toggle_label.config(text="☑ Hide out-of-stock")
            else:
                self.filter_toggle_label.config(text="🔲 Hide out-of-stock")
        
        # Re-display results with filter applied
        if hasattr(self, 'search_results') and self.search_results:
            self._display_search_results(self.search_results)
    
    def _display_search_results(self, products: list):
        """Display search results in scrollable grid."""
        # Clear previous results
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
        
        # Filter by product group if selected
        filtered_products = products
        if self.selected_product_group is not None:
            filtered_products = [
                p for p in products 
                if p.get('product_group_id') == self.selected_product_group
            ]
        
        # Store original products for reference
        self.search_results = products
        
        # Update group indicator after filtering
        self._update_group_indicator()
        
        if hasattr(self, 'search_status_label'):
            total_count = len(products)
            shown_count = len(filtered_products)
            status_text = f"Found {total_count} product(s)"
            if self.selected_product_group is not None or self.hide_out_of_stock:
                status_text += f" (showing {shown_count})"
            self.search_status_label.config(text=status_text, fg=Theme.STATUS_SUCCESS)
        
        # Configure grid columns
        cols = self.search_results_grid_cols
        for i in range(cols):
            self.search_results_frame.columnconfigure(i, weight=1, uniform="equal")
        
        # Store product data for filtering after stock is loaded
        self._product_data_for_filtering = {}
        
        # Load stock and images in background thread for each filtered product
        row = 0
        col = 0
        for idx, product in enumerate(filtered_products):
            product_id = product.get('id')
            product_name = product.get('name', 'Unknown Product')
            picture_file_name = product.get('picture_file_name')
            
            # Create product item frame (grid card style)
            item_frame = tk.Frame(
                self.search_results_frame, 
                bg=Theme.BUTTON_CONFIG, 
                relief=tk.RAISED,
                borderwidth=2
            )
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            item_frame.columnconfigure(0, weight=1)
            
            # Product image (top)
            image_frame = tk.Frame(item_frame, bg=Theme.BUTTON_CONFIG, height=120)
            image_frame.pack(fill=tk.X, padx=5, pady=5)
            image_frame.pack_propagate(False)
            
            image_label = tk.Label(
                image_frame,
                bg=Theme.BUTTON_CONFIG,
                height=8
            )
            image_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Product info (bottom)
            info_frame = tk.Frame(item_frame, bg=Theme.BUTTON_CONFIG)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Product name
            name_label = tk.Label(
                info_frame,
                text=product_name.upper(),
                font=Theme.get_info_font(),
                bg=Theme.BUTTON_CONFIG,
                fg='white',
                wraplength=150,
                justify=tk.CENTER
            )
            name_label.pack(pady=2)
            
            # Stock label (will be updated async)
            stock_label = tk.Label(
                info_frame,
                text="Stock: ...",
                font=Theme.get_config_font(),
                bg=Theme.BUTTON_CONFIG,
                fg='white',
            )
            stock_label.pack(pady=2)
            
            # Store reference for filtering
            self._product_data_for_filtering[product_id] = {
                'frame': item_frame,
                'stock': None  # Will be updated
            }
            
            # Bind click to show product detail
            def make_click_handler(pid):
                return lambda e: self._show_product_detail(pid)
            
            for widget in [item_frame, image_label, name_label, stock_label]:
                widget.bind('<Button-1>', make_click_handler(product_id))
            
            # Hover effect
            def make_hover_handlers(frame, img_frame, info_frame, name_lbl, stock_lbl):
                def enter(e): 
                    frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    img_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    info_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    name_lbl.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    stock_lbl.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                    image_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d'))
                def leave(e): 
                    frame.config(bg=Theme.BUTTON_CONFIG)
                    img_frame.config(bg=Theme.BUTTON_CONFIG)
                    info_frame.config(bg=Theme.BUTTON_CONFIG)
                    name_lbl.config(bg=Theme.BUTTON_CONFIG)
                    stock_lbl.config(bg=Theme.BUTTON_CONFIG)
                    image_label.config(bg=Theme.BUTTON_CONFIG)
                return enter, leave
            
            enter_handler, leave_handler = make_hover_handlers(item_frame, image_frame, info_frame, name_label, stock_label)
            for widget in [item_frame, image_label, name_label, stock_label]:
                widget.bind('<Enter>', enter_handler)
                widget.bind('<Leave>', leave_handler)
            
            # Load stock and image in background thread
            threading.Thread(
                target=self._load_product_info_for_search_result_grid,
                args=(product_id, product_name, picture_file_name, stock_label, image_label),
                daemon=True
            ).start()
            
            # Move to next grid position
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # Update scroll region
        self.search_canvas.update_idletasks()
        self.search_canvas.configure(scrollregion=self.search_canvas.bbox("all"))
    
    def _load_product_info_for_search_result_grid(self, product_id: int, product_name: str, 
                                                  picture_file_name: Optional[str], 
                                                  stock_label: tk.Label, image_label: tk.Label):
        """Load stock and image for a search result grid item in background thread."""
        import time
        
        # Get stock amount with retries (like in _process_barcode_thread)
        stock_amount = 0
        for attempt in range(3):
            try:
                stock = self.grocy_api.get_stock(product_id)
                if isinstance(stock, list) and len(stock) > 0:
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                    if stock_amount > 0:
                        break
                elif isinstance(stock, dict):
                    stock_amount = stock.get('amount', 0)
                    if stock_amount > 0:
                        break
                    # Also try 'stock_amount' key
                    stock_amount = stock.get('stock_amount', stock_amount)
                    if stock_amount > 0:
                        break
            except Exception as e:
                print(f"  Error getting stock for product {product_id}: {e}")
            
            if attempt < 2:
                time.sleep(0.3)
        
        # Store stock for filtering
        if hasattr(self, '_product_data_for_filtering') and product_id in self._product_data_for_filtering:
            self._product_data_for_filtering[product_id]['stock'] = stock_amount
        
        # Update stock label
        stock_text = f"Stock: {stock_amount}" if stock_amount > 0 else "Stock: 0"
        self.root.after(0, lambda: stock_label.config(text=stock_text))
        
        # Hide item if out-of-stock and filter is enabled
        if self.hide_out_of_stock and stock_amount == 0:
            if hasattr(self, '_product_data_for_filtering') and product_id in self._product_data_for_filtering:
                self.root.after(0, lambda: self._product_data_for_filtering[product_id]['frame'].grid_remove())
            return
        
        # Show item if it was hidden
        if hasattr(self, '_product_data_for_filtering') and product_id in self._product_data_for_filtering:
            self.root.after(0, lambda: self._product_data_for_filtering[product_id]['frame'].grid())
        
        # Load product image
        if picture_file_name:
            base_url = self.grocy_api.base_url
            urls_to_try = build_grocy_image_urls(
                base_url, 
                picture_file_name, 
                product_id, 
                self.grocy_api.api_key
            )
            
            for url in urls_to_try:
                try:
                    response = requests.get(url, timeout=5, headers={'GROCY-API-KEY': self.grocy_api.api_key})
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        
                        # Handle transparent PNGs
                        if img.mode == 'RGBA':
                            bg_color = tuple(int(Theme.BUTTON_CONFIG[i:i+2], 16) for i in (1, 3, 5))
                            background = Image.new('RGB', img.size, bg_color)
                            background.paste(img, mask=img.split()[3])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize to thumbnail size for grid (larger than list)
                        img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Update image label in main thread
                        self.root.after(0, lambda p=photo: image_label.config(image=p, bg=Theme.BUTTON_CONFIG) or setattr(image_label, 'image', p))
                        break
                except Exception as e:
                    print(f"  Error loading image for product {product_id}: {e}")
                    continue
    
    def _show_product_detail(self, product_id: int):
        """Navigate to product detail page."""
        self._clear_pages()
        self.current_page = 'product_detail'
        self._setup_product_detail_page(product_id)
    
    def _setup_product_detail_page(self, product_id: int):
        """Setup product detail page with info, stock, and action buttons."""
        # Hide main page widgets
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()
        
        # Create detail page frame
        self.product_detail_frame = tk.Frame(self.main_frame, bg=Theme.BACKGROUND)
        self.product_detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get product info
        product = self.grocy_api.get_product_by_id(product_id)
        if not product:
            self._show_error("Product not found")
            self._setup_main_page()
            return
        
        product_name = product.get('name', 'Unknown Product')
        picture_file_name = product.get('picture_file_name')
        
        # Get stock with retries (like in _process_barcode_thread)
        import time
        stock_amount = 0
        for attempt in range(3):
            try:
                stock = self.grocy_api.get_stock(product_id)
                if isinstance(stock, list) and len(stock) > 0:
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                    if stock_amount > 0:
                        break
                elif isinstance(stock, dict):
                    stock_amount = stock.get('amount', 0)
                    if stock_amount > 0:
                        break
                    # Also try 'stock_amount' key
                    stock_amount = stock.get('stock_amount', stock_amount)
                    if stock_amount > 0:
                        break
            except Exception as e:
                print(f"  Error getting stock for product {product_id}: {e}")
            
            if attempt < 2:
                time.sleep(0.3)
        
        # Header with back button
        header_frame = tk.Frame(self.product_detail_frame, bg=Theme.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Back button
        back_frame = tk.Frame(header_frame, bg=Theme.BUTTON_CONFIG)
        icon_loader = get_icon_loader()
        back_icon_img = icon_loader.load_icon('arrow_left', size=(18, 18), color='white')
        if back_icon_img:
            back_icon_label = tk.Label(
                back_frame,
                image=back_icon_img,
                bg=Theme.BUTTON_CONFIG,
            )
            back_icon_label.image = back_icon_img  # Keep reference
            back_icon_label.pack(side=tk.LEFT, padx=(8, 3), pady=5)
        back_label = tk.Label(
            back_frame,
            text="BACK",
            font=Theme.get_config_font(),
            bg=Theme.BUTTON_CONFIG,
            fg='white',
        )
        back_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        back_frame.pack(side=tk.LEFT)
        back_label.bind('<Button-1>', lambda e: self._show_search_page())
        back_frame.bind('<Button-1>', lambda e: self._show_search_page())
        if back_icon_img:
            back_icon_label.bind('<Button-1>', lambda e: self._show_search_page())
        
        # Hover effect for back button
        def back_enter(e): back_frame.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')); back_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')); (back_icon_label.config(bg=getattr(Theme, 'BUTTON_CONFIG_HOVER', '#2d2d2d')) if back_icon_img else None)
        def back_leave(e): back_frame.config(bg=Theme.BUTTON_CONFIG); back_label.config(bg=Theme.BUTTON_CONFIG); (back_icon_label.config(bg=Theme.BUTTON_CONFIG) if back_icon_img else None)
        back_label.bind('<Enter>', back_enter)
        back_label.bind('<Leave>', back_leave)
        back_frame.bind('<Enter>', back_enter)
        back_frame.bind('<Leave>', back_leave)
        if back_icon_img:
            back_icon_label.bind('<Enter>', back_enter)
            back_icon_label.bind('<Leave>', back_leave)
        
        # Content frame
        content_frame = tk.Frame(self.product_detail_frame, bg=Theme.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Product image
        image_frame = tk.Frame(content_frame, bg=Theme.BACKGROUND)
        image_frame.pack(pady=20)
        
        detail_image_label = tk.Label(image_frame, bg=Theme.BACKGROUND)
        detail_image_label.pack()
        
        # Load product image
        if picture_file_name:
            base_url = self.grocy_api.base_url
            urls_to_try = build_grocy_image_urls(
                base_url, 
                picture_file_name, 
                product_id, 
                self.grocy_api.api_key
            )
            
            for url in urls_to_try:
                try:
                    response = requests.get(url, timeout=5, headers={'GROCY-API-KEY': self.grocy_api.api_key})
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        if img.mode == 'RGBA':
                            bg_color = tuple(int(Theme.BACKGROUND[i:i+2], 16) for i in (1, 3, 5))
                            background = Image.new('RGB', img.size, bg_color)
                            background.paste(img, mask=img.split()[3])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.thumbnail(Theme.PRODUCT_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        detail_image_label.config(image=photo, bg=Theme.BACKGROUND)
                        detail_image_label.image = photo
                        break
                except:
                    continue
        
        # Product name
        name_label = tk.Label(
            content_frame,
            text=product_name.upper(),
            font=Theme.get_title_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_PRIMARY
        )
        name_label.pack(pady=10)
        
        # Stock info
        stock_label = tk.Label(
            content_frame,
            text=f"STOCK: {stock_amount}",
            font=Theme.get_info_font(),
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_SECONDARY
        )
        stock_label.pack(pady=10)
        
        # Action buttons (horizontal layout for smaller screens)
        actions_frame = tk.Frame(content_frame, bg=Theme.BACKGROUND)
        actions_frame.pack(pady=30)
        
        # Add button
        add_frame = tk.Frame(actions_frame, bg=Theme.BUTTON_ADD)
        add_content = tk.Frame(add_frame, bg=Theme.BUTTON_ADD)
        add_content.pack(padx=15, pady=12)
        
        icon_loader = get_icon_loader()
        plus_icon = icon_loader.load_icon('plus', size=(24, 24), color='white')
        if plus_icon:
            add_icon = tk.Label(add_content, image=plus_icon, bg=Theme.BUTTON_ADD)
            add_icon.image = plus_icon
            add_icon.pack(pady=(0, 3))
        
        add_label = tk.Label(
            add_content,
            text="ADD",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_ADD,
            fg='white',
        )
        add_label.pack()
        add_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        add_label.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'add'))
        add_frame.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'add'))
        add_content.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'add'))
        if plus_icon:
            add_icon.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'add'))
        
        def add_enter(e): add_frame.config(bg=Theme.BUTTON_ADD_HOVER); add_label.config(bg=Theme.BUTTON_ADD_HOVER); add_content.config(bg=Theme.BUTTON_ADD_HOVER); (add_icon.config(bg=Theme.BUTTON_ADD_HOVER) if plus_icon else None)
        def add_leave(e): add_frame.config(bg=Theme.BUTTON_ADD); add_label.config(bg=Theme.BUTTON_ADD); add_content.config(bg=Theme.BUTTON_ADD); (add_icon.config(bg=Theme.BUTTON_ADD) if plus_icon else None)
        add_label.bind('<Enter>', add_enter)
        add_label.bind('<Leave>', add_leave)
        add_frame.bind('<Enter>', add_enter)
        add_frame.bind('<Leave>', add_leave)
        add_content.bind('<Enter>', add_enter)
        add_content.bind('<Leave>', add_leave)
        if plus_icon:
            add_icon.bind('<Enter>', add_enter)
            add_icon.bind('<Leave>', add_leave)
        
        # Open button
        open_frame = tk.Frame(actions_frame, bg=Theme.BUTTON_OPEN)
        open_content = tk.Frame(open_frame, bg=Theme.BUTTON_OPEN)
        open_content.pack(padx=15, pady=12)
        
        box_icon = icon_loader.load_icon('box', size=(24, 24), color='white')
        if box_icon:
            open_icon = tk.Label(open_content, image=box_icon, bg=Theme.BUTTON_OPEN)
            open_icon.image = box_icon
            open_icon.pack(pady=(0, 3))
        
        open_label = tk.Label(
            open_content,
            text="OPEN",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_OPEN,
            fg='white',
        )
        open_label.pack()
        open_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        open_label.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'open'))
        open_frame.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'open'))
        open_content.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'open'))
        if box_icon:
            open_icon.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'open'))
        
        def open_enter(e): open_frame.config(bg=Theme.BUTTON_OPEN_HOVER); open_label.config(bg=Theme.BUTTON_OPEN_HOVER); open_content.config(bg=Theme.BUTTON_OPEN_HOVER); (open_icon.config(bg=Theme.BUTTON_OPEN_HOVER) if box_icon else None)
        def open_leave(e): open_frame.config(bg=Theme.BUTTON_OPEN); open_label.config(bg=Theme.BUTTON_OPEN); open_content.config(bg=Theme.BUTTON_OPEN); (open_icon.config(bg=Theme.BUTTON_OPEN) if box_icon else None)
        open_label.bind('<Enter>', open_enter)
        open_label.bind('<Leave>', open_leave)
        open_frame.bind('<Enter>', open_enter)
        open_frame.bind('<Leave>', open_leave)
        open_content.bind('<Enter>', open_enter)
        open_content.bind('<Leave>', open_leave)
        if box_icon:
            open_icon.bind('<Enter>', open_enter)
            open_icon.bind('<Leave>', open_leave)
        
        # Deduct button
        deduct_frame = tk.Frame(actions_frame, bg=Theme.BUTTON_DEDUCT)
        deduct_content = tk.Frame(deduct_frame, bg=Theme.BUTTON_DEDUCT)
        deduct_content.pack(padx=15, pady=12)
        
        minus_icon = icon_loader.load_icon('minus', size=(24, 24), color='white')
        if minus_icon:
            deduct_icon = tk.Label(deduct_content, image=minus_icon, bg=Theme.BUTTON_DEDUCT)
            deduct_icon.image = minus_icon
            deduct_icon.pack(pady=(0, 3))
        
        deduct_label = tk.Label(
            deduct_content,
            text="DEDUCT",
            font=Theme.get_button_font(),
            bg=Theme.BUTTON_DEDUCT,
            fg='white',
        )
        deduct_label.pack()
        deduct_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        deduct_label.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'deduct'))
        deduct_frame.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'deduct'))
        deduct_content.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'deduct'))
        if minus_icon:
            deduct_icon.bind('<Button-1>', lambda e: self._perform_product_action(product_id, 'deduct'))
        
        def deduct_enter(e): deduct_frame.config(bg=Theme.BUTTON_DEDUCT_HOVER); deduct_label.config(bg=Theme.BUTTON_DEDUCT_HOVER); deduct_content.config(bg=Theme.BUTTON_DEDUCT_HOVER); (deduct_icon.config(bg=Theme.BUTTON_DEDUCT_HOVER) if minus_icon else None)
        def deduct_leave(e): deduct_frame.config(bg=Theme.BUTTON_DEDUCT); deduct_label.config(bg=Theme.BUTTON_DEDUCT); deduct_content.config(bg=Theme.BUTTON_DEDUCT); (deduct_icon.config(bg=Theme.BUTTON_DEDUCT) if minus_icon else None)
        deduct_label.bind('<Enter>', deduct_enter)
        deduct_label.bind('<Leave>', deduct_leave)
        deduct_frame.bind('<Enter>', deduct_enter)
        deduct_frame.bind('<Leave>', deduct_leave)
        deduct_content.bind('<Enter>', deduct_enter)
        deduct_content.bind('<Leave>', deduct_leave)
        if minus_icon:
            deduct_icon.bind('<Enter>', deduct_enter)
            deduct_icon.bind('<Leave>', deduct_leave)
    
    def _perform_product_action(self, product_id: int, action: str):
        """Perform action (add/open/deduct) on product."""
        # Perform action in background thread
        threading.Thread(target=self._action_thread, args=(product_id, action), daemon=True).start()
    
    def _action_thread(self, product_id: int, action: str):
        """Perform action in background thread."""
        try:
            if action == 'add':
                result = self.grocy_api.add_to_stock(product_id, amount=1.0)
            elif action == 'open':
                result = self.grocy_api.open_product(product_id, amount=1.0)
            elif action == 'deduct':
                result = self.grocy_api.deduct_from_stock(product_id, amount=1.0)
            else:
                return
            
            if result:
                # Get updated stock
                import time
                time.sleep(0.3)
                stock = self.grocy_api.get_stock(product_id)
                if isinstance(stock, list) and len(stock) > 0:
                    stock_amount = sum(entry.get('amount', 0) for entry in stock if isinstance(entry, dict))
                elif isinstance(stock, dict):
                    stock_amount = stock.get('amount', 0)
                else:
                    stock_amount = 0
                
                # Get product info
                product = self.grocy_api.get_product_by_id(product_id)
                product_name = product.get('name', 'Unknown Product') if product else 'Unknown Product'
                
                # Show success and refresh detail page
                self.root.after(0, self._show_action_success, product_id, product_name, stock_amount, action)
            else:
                self.root.after(0, lambda: self._show_action_error(f"Failed to {action} stock"))
        except Exception as e:
            self.root.after(0, lambda: self._show_action_error(f"Error: {str(e)}"))
    
    def _show_action_success(self, product_id: int, product_name: str, stock_amount: float, action: str):
        """Show success message and refresh detail page."""
        # Refresh the detail page with updated stock
        self._setup_product_detail_page(product_id)
        
        # Show temporary success message as overlay (floating above content)
        success_frame = tk.Frame(self.product_detail_frame, bg=Theme.STATUS_SUCCESS, relief=tk.RAISED, borderwidth=2)
        success_label = tk.Label(
            success_frame,
            text=f"{action.upper()} SUCCESSFUL\nNEW STOCK: {stock_amount}",
            font=Theme.get_status_font(),
            bg=Theme.STATUS_SUCCESS,
            fg='white',
            wraplength=600,  # Allow text wrapping for long messages
            justify=tk.CENTER
        )
        success_label.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
        
        # Place overlay at the top center, floating above content (doesn't affect layout)
        success_frame.place(relx=0.5, rely=0.1, anchor=tk.N, relwidth=0.9)
        
        # Remove success message after 3 seconds
        self.root.after(3000, lambda: success_frame.destroy())
    
    def _show_action_error(self, message: str):
        """Show error message on detail page."""
        error_frame = tk.Frame(self.product_detail_frame, bg=Theme.STATUS_ERROR, relief=tk.RAISED, borderwidth=2)
        error_label = tk.Label(
            error_frame,
            text=f"ERROR: {message.upper()}",
            font=Theme.get_status_font(),
            bg=Theme.STATUS_ERROR,
            fg='white',
            wraplength=600,  # Allow text wrapping for long messages
            justify=tk.CENTER
        )
        error_label.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
        
        # Place overlay at the top center, floating above content
        error_frame.place(relx=0.5, rely=0.1, anchor=tk.N, relwidth=0.9)
        
        # Remove error message after 3 seconds
        self.root.after(3000, lambda: error_frame.destroy())
