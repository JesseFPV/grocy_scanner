"""USB barcode scanner input handling."""
import threading
import sys
from typing import Optional, Callable

# Try to import select for non-blocking stdin reads (fallback method)
try:
    import select
    HAS_SELECT = True
except ImportError:
    HAS_SELECT = False


class BarcodeScanner:
    """Handles input from USB barcode scanner (keyboard emulation)."""
    
    def __init__(self, callback: Callable[[str], None], root_widget=None):
        """
        Initialize barcode scanner.
        
        Args:
            callback: Function to call when a barcode is scanned (receives barcode string)
            root_widget: Optional tkinter widget to bind keyboard events to
        """
        self.callback = callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.buffer = ""
        self.root_widget = root_widget
        
        # If we have a tkinter widget, use keyboard bindings (preferred method)
        if self.root_widget:
            self._setup_keyboard_bindings()
    
    def _setup_keyboard_bindings(self):
        """Setup keyboard event bindings for barcode scanner input."""
        import time
        
        def on_key(event):
            # Barcode scanners typically send characters very quickly
            # We accumulate them and process on Enter/Return
            if event.keysym == 'Return' or event.keysym == 'KP_Enter':
                # ENTER pressed - process the barcode
                if self.buffer.strip():
                    barcode = self.buffer.strip()
                    self.buffer = ""  # Clear buffer immediately
                    self.callback(barcode)
                else:
                    self.buffer = ""  # Clear buffer even if empty
            elif event.keysym in ['BackSpace', 'Delete']:
                # Handle backspace/delete
                if self.buffer:
                    self.buffer = self.buffer[:-1]
            elif event.char and event.char.isprintable() and len(event.char) == 1:
                # Add printable character to buffer
                self.buffer += event.char
        
        if self.root_widget:
            # Bind to root and all children to catch all keyboard input
            self.root_widget.bind_all('<KeyPress>', on_key)
            # Ensure root widget can receive focus
            self.root_widget.focus_set()
            # Make sure it stays focused
            self.root_widget.bind('<FocusOut>', lambda e: self.root_widget.focus_set())
    
    def _read_input(self):
        """Read input from stdin (fallback method)."""
        buffer = ""
        while self.running:
            try:
                # Use select for non-blocking read if available
                if HAS_SELECT:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        char = sys.stdin.read(1)
                        if char:
                            if char == '\n' or char == '\r':
                                # End of barcode
                                if buffer.strip():
                                    self.callback(buffer.strip())
                                buffer = ""
                            else:
                                buffer += char
                else:
                    # Fallback: blocking read (less ideal)
                    char = sys.stdin.read(1)
                    if char:
                        if char == '\n' or char == '\r':
                            if buffer.strip():
                                self.callback(buffer.strip())
                            buffer = ""
                        else:
                            buffer += char
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                print(f"Scanner error: {e}")
                break
    
    def start(self):
        """Start listening for barcode scans."""
        if self.running:
            return
        
        self.running = True
        
        # Only start stdin thread if we don't have keyboard bindings
        if not self.root_widget:
            self.thread = threading.Thread(target=self._read_input, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop listening for barcode scans."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

