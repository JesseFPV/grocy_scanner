#!/usr/bin/env python3
"""Test script to verify button colors."""
import tkinter as tk
from themes.portal_theme import PortalTheme as Theme

root = tk.Tk()
root.title("Color Test")
root.configure(bg=Theme.BACKGROUND)

# Create test buttons
add_btn = tk.Button(
    root,
    text="ADD TO STOCK",
    bg=Theme.BUTTON_ADD,
    fg='white',
    width=20,
    height=3
)
add_btn.pack(pady=10)

open_btn = tk.Button(
    root,
    text="OPEN PRODUCT",
    bg=Theme.BUTTON_OPEN,
    fg='white',
    width=20,
    height=3
)
open_btn.pack(pady=10)

deduct_btn = tk.Button(
    root,
    text="DEDUCT STOCK",
    bg=Theme.BUTTON_DEDUCT,
    fg='white',
    width=20,
    height=3
)
deduct_btn.pack(pady=10)

# Show color values
info = tk.Label(
    root,
    text=f"ADD: {Theme.BUTTON_ADD}\nOPEN: {Theme.BUTTON_OPEN}\nDEDUCT: {Theme.BUTTON_DEDUCT}",
    bg=Theme.BACKGROUND,
    fg='white',
    font=('Arial', 12)
)
info.pack(pady=20)

print(f"BUTTON_ADD: {Theme.BUTTON_ADD}")
print(f"BUTTON_OPEN: {Theme.BUTTON_OPEN}")
print(f"BUTTON_DEDUCT: {Theme.BUTTON_DEDUCT}")

root.mainloop()

