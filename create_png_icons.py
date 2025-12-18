#!/usr/bin/env python3
"""Create PNG icons from SVG using available tools."""
import os
import subprocess
import sys

def create_png_from_svg(svg_path, png_path, size=(28, 28)):
    """Create PNG from SVG using available command-line tools."""
    # Try rsvg-convert (librsvg)
    try:
        result = subprocess.run(
            ['rsvg-convert', '-w', str(size[0]), '-h', str(size[1]), svg_path, '-o', png_path],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0 and os.path.exists(png_path):
            print(f"✓ Created {os.path.basename(png_path)} using rsvg-convert")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass
    
    # Try inkscape
    try:
        result = subprocess.run(
            ['inkscape', '--export-type=png', 
             f'--export-width={size[0]}', 
             f'--export-height={size[1]}', 
             f'--export-filename={png_path}', 
             svg_path],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0 and os.path.exists(png_path):
            print(f"✓ Created {os.path.basename(png_path)} using inkscape")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass
    
    return False

def main():
    icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
    
    # Icons to convert
    icons_to_convert = [
        ('plus.svg', (28, 28)),
        ('minus.svg', (28, 28)),
        ('box.svg', (28, 28)),
    ]
    
    print("Creating PNG icons from SVG...")
    
    for svg_file, size in icons_to_convert:
        svg_path = os.path.join(icon_dir, svg_file)
        png_file = svg_file.replace('.svg', '.png')
        png_path = os.path.join(icon_dir, png_file)
        
        if not os.path.exists(svg_path):
            print(f"✗ SVG not found: {svg_file}")
            continue
        
        if os.path.exists(png_path):
            print(f"○ PNG already exists: {png_file}")
            continue
        
        if create_png_from_svg(svg_path, png_path, size):
            print(f"  Created {png_file}")
        else:
            print(f"✗ Failed to create {png_file} (install rsvg-convert or inkscape)")

if __name__ == '__main__':
    main()

