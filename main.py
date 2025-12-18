#!/usr/bin/env python3
"""Main entry point for Intake."""
import sys
import tkinter as tk
from config import Config
from ui import GrocyScannerUI
from scanner import BarcodeScanner


def main():
    """Main function."""
    # Load configuration
    config = Config()
    
    # Create root window
    root = tk.Tk()
    
    # Create UI
    ui = GrocyScannerUI(root, config)
    
    # Setup barcode scanner (pass root widget for keyboard bindings)
    scanner = BarcodeScanner(ui.process_barcode, root_widget=root)
    scanner.start()
    
    # Handle window close
    def on_closing():
        scanner.stop()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Run main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        scanner.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()

