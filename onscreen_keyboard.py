"""Onscreen keyboard widget for touchscreen devices."""
import tkinter as tk
from typing import Callable, Optional
from theme import Theme
from icon_loader import get_icon_loader


class OnScreenKeyboard:
    """Onscreen keyboard widget for touchscreen input."""
    
    def __init__(self, parent: tk.Widget, target_entry: Optional[tk.Entry] = None, 
                 callback: Optional[Callable[[str], None]] = None):
        """
        Initialize onscreen keyboard.
        
        Args:
            parent: Parent widget
            target_entry: Entry widget to send input to (optional)
            callback: Callback function called when Enter is pressed (optional)
        """
        self.parent = parent
        self.target_entry = target_entry
        self.callback = callback
        self.frame = None
        self.shift_pressed = False
        self.caps_lock = False
        
    def show(self, target_entry: Optional[tk.Entry] = None):
        """Show the keyboard."""
        if target_entry:
            self.target_entry = target_entry
        
        if self.frame:
            self.frame.destroy()
        
        self.frame = tk.Frame(self.parent, bg=Theme.BACKGROUND, relief=tk.RAISED, borderwidth=2)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Keyboard layout
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'BACKSPACE'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '-', '_'],
            [':', '/', '?', '&', '=', '@', '#', '%', '+'],
            ['Space', 'Enter', 'BACKSPACE']
        ]
        
        # Use dark gray/black background for all keys (like other buttons)
        KEY_BG = '#000000'  # Black
        KEY_FG = '#ffffff'  # White
        
        for row_idx, row in enumerate(rows):
            row_frame = tk.Frame(self.frame, bg=Theme.BACKGROUND)
            row_frame.pack(pady=2)
            
            for key in row:
                # Use Frame-based approach for macOS compatibility (like other buttons)
                key_frame = tk.Frame(row_frame, bg=KEY_BG, cursor='hand2')
                
                if key == 'Space':
                    key_label = tk.Label(
                        key_frame,
                        text='Space',
                        bg=KEY_BG,
                        fg=KEY_FG,
                        font=Theme.get_config_font(),
                        cursor='hand2',
                        width=15,
                        height=2
                    )
                    key_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    key_label.bind('<Button-1>', lambda e: self._insert_char(' '))
                    key_frame.bind('<Button-1>', lambda e: self._insert_char(' '))
                elif key == 'Enter':
                    key_label = tk.Label(
                        key_frame,
                        text='Enter',
                        bg=KEY_BG,
                        fg=KEY_FG,
                        font=Theme.get_config_font(),
                        cursor='hand2',
                        width=10,
                        height=2
                    )
                    key_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    key_label.bind('<Button-1>', lambda e: self._on_enter())
                    key_frame.bind('<Button-1>', lambda e: self._on_enter())
                elif key == 'SHIFT':
                    icon_loader = get_icon_loader()
                    shift_icon = icon_loader.load_icon('shift', size=(16, 16), color='white')
                    if shift_icon:
                        key_label = tk.Label(
                            key_frame,
                            image=shift_icon,
                            bg=KEY_BG,
                            fg=KEY_FG,
                            cursor='hand2'
                        )
                        key_label.image = shift_icon  # Keep reference
                    else:
                        key_label = tk.Label(
                            key_frame,
                            text='SHIFT',
                            bg=KEY_BG,
                            fg=KEY_FG,
                            font=Theme.get_config_font(),
                            cursor='hand2',
                            width=5,
                            height=2
                        )
                    key_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    key_label.bind('<Button-1>', lambda e: self._toggle_shift())
                    key_frame.bind('<Button-1>', lambda e: self._toggle_shift())
                elif key == 'BACKSPACE':
                    icon_loader = get_icon_loader()
                    backspace_icon = icon_loader.load_icon('backspace', size=(16, 16), color='white')
                    if backspace_icon:
                        key_label = tk.Label(
                            key_frame,
                            image=backspace_icon,
                            bg=KEY_BG,
                            fg=KEY_FG,
                            cursor='hand2'
                        )
                        key_label.image = backspace_icon  # Keep reference
                    else:
                        key_label = tk.Label(
                            key_frame,
                            text='DEL',
                            bg=KEY_BG,
                            fg=KEY_FG,
                            font=Theme.get_config_font(),
                            cursor='hand2',
                            width=5,
                            height=2
                        )
                    key_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    key_label.bind('<Button-1>', lambda e: self._backspace())
                    key_frame.bind('<Button-1>', lambda e: self._backspace())
                else:
                    # Special characters (URL symbols) are displayed as-is, no case conversion
                    if key in [':', '/', '?', '&', '=', '@', '#', '%', '+', '.', '-', '_']:
                        display_char = key
                    else:
                        display_char = key.upper() if (self.shift_pressed or self.caps_lock) else key.lower()
                    key_label = tk.Label(
                        key_frame,
                        text=display_char,
                        bg=KEY_BG,
                        fg=KEY_FG,
                        font=Theme.get_config_font(),
                        cursor='hand2',
                        width=4,
                        height=2
                    )
                    key_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    key_label.bind('<Button-1>', lambda e, c=key: self._insert_char(c))
                    key_frame.bind('<Button-1>', lambda e, c=key: self._insert_char(c))
                
                # Hover effect
                def make_hover_handlers(frame, label):
                    def enter(e): 
                        frame.config(bg='#1a1a1a')
                        label.config(bg='#1a1a1a')
                    def leave(e): 
                        frame.config(bg=KEY_BG)
                        label.config(bg=KEY_BG)
                    return enter, leave
                
                enter_handler, leave_handler = make_hover_handlers(key_frame, key_label)
                key_label.bind('<Enter>', enter_handler)
                key_label.bind('<Leave>', leave_handler)
                key_frame.bind('<Enter>', enter_handler)
                key_frame.bind('<Leave>', leave_handler)
                
                key_frame.pack(side=tk.LEFT, padx=2)
    
    def hide(self):
        """Hide the keyboard."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def _insert_char(self, char: str):
        """Insert a character into the target entry."""
        if self.target_entry:
            # Special characters (URL symbols) are inserted as-is, no case conversion
            if char in [':', '/', '?', '&', '=', '@', '#', '%', '+', '.', '-', '_']:
                display_char = char
            else:
                display_char = char.upper() if (self.shift_pressed or self.caps_lock) else char.lower()
            current_pos = self.target_entry.index(tk.INSERT)
            self.target_entry.insert(current_pos, display_char)
            self.target_entry.focus_set()
            
            # Release shift after one character
            if self.shift_pressed:
                self.shift_pressed = False
                self.show()
    
    def _backspace(self):
        """Delete last character."""
        if self.target_entry:
            current_pos = self.target_entry.index(tk.INSERT)
            if current_pos > 0:
                self.target_entry.delete(current_pos - 1, current_pos)
            self.target_entry.focus_set()
    
    def _toggle_shift(self):
        """Toggle shift/caps lock."""
        if self.shift_pressed:
            self.caps_lock = not self.caps_lock
            self.shift_pressed = False
        else:
            self.shift_pressed = True
        self.show()
    
    def _on_enter(self):
        """Handle Enter key press."""
        if self.callback and self.target_entry:
            value = self.target_entry.get()
            self.callback(value)
        elif self.target_entry:
            # Simulate Enter key
            self.target_entry.event_generate('<Return>')
    
    def is_visible(self) -> bool:
        """Check if keyboard is visible."""
        return self.frame is not None

