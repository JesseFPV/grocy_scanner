#!/usr/bin/env python3
"""Test script for barcode scanner input."""
import tkinter as tk
from scanner import BarcodeScanner

def on_barcode_scanned(barcode):
    """Callback when barcode is scanned."""
    print(f"✓ Barcode scanned: {barcode}")

root = tk.Tk()
root.title("Barcode Scanner Test")
root.geometry("400x200")

label = tk.Label(
    root,
    text="Scan a barcode with your scanner...\n(Press ENTER after scanning)",
    font=('Arial', 16),
    pady=50
)
label.pack()

scanner = BarcodeScanner(on_barcode_scanned, root_widget=root)
scanner.start()

root.focus_set()
root.focus_force()

print("Barcode scanner test started.")
print("Scan a barcode - it should appear below:")
print("-" * 50)

root.mainloop()

