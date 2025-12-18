#!/usr/bin/env python3
"""Convert SVG icons to PNG format for better compatibility."""
import os
from PIL import Image
from io import BytesIO
import subprocess

def convert_svg_to_png(svg_path: str, png_path: str, size: tuple = (24, 24)):
    """Convert SVG to PNG using available tools."""
    # Try rsvg-convert first (librsvg, common on Linux)
    try:
        result = subprocess.run(
            ['rsvg-convert', '-w', str(size[0]), '-h', str(size[1]), svg_path],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            img = Image.open(BytesIO(result.stdout))
            img.save(png_path, 'PNG')
            print(f"✓ Converted {os.path.basename(svg_path)} -> {os.path.basename(png_path)}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        pass
    
    # Try inkscape
    try:
        result = subprocess.run(
            ['inkscape', '--export-type=png', f'--export-width={size[0]}', 
             f'--export-height={size[1]}', f'--export-filename={png_path}', svg_path],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0 and os.path.exists(png_path):
            print(f"✓ Converted {os.path.basename(svg_path)} -> {os.path.basename(png_path)}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        pass
    
    # Try cairosvg (Python library)
    try:
        import cairosvg
        png_data = cairosvg.svg2png(url=svg_path, output_width=size[0], output_height=size[1])
        img = Image.open(BytesIO(png_data))
        img.save(png_path, 'PNG')
        print(f"✓ Converted {os.path.basename(svg_path)} -> {os.path.basename(png_path)}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"✗ Error converting {svg_path}: {e}")
    
    return False

def main():
    """Convert all SVG icons to PNG."""
    icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
    
    if not os.path.exists(icon_dir):
        print(f"Error: Icons directory not found: {icon_dir}")
        return
    
    svg_files = [f for f in os.listdir(icon_dir) if f.endswith('.svg')]
    
    if not svg_files:
        print("No SVG files found in icons directory")
        return
    
    print(f"Found {len(svg_files)} SVG files to convert...")
    
    converted = 0
    failed = 0
    
    for svg_file in svg_files:
        svg_path = os.path.join(icon_dir, svg_file)
        png_file = svg_file.replace('.svg', '.png')
        png_path = os.path.join(icon_dir, png_file)
        
        if convert_svg_to_png(svg_path, png_path):
            converted += 1
        else:
            print(f"✗ Failed to convert {svg_file}")
            failed += 1
    
    print(f"\nConversion complete: {converted} succeeded, {failed} failed")
    
    if failed > 0:
        print("\nNote: Install one of these tools to convert SVG to PNG:")
        print("  - librsvg-utils (rsvg-convert)")
        print("  - inkscape")
        print("  - cairosvg (pip install cairosvg)")

if __name__ == '__main__':
    main()

