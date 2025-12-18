"""Icon loader for SVG/PNG icons - converts to PhotoImage for Tkinter."""
import tkinter as tk
from PIL import Image, ImageTk
import os
from io import BytesIO
from typing import Optional, Dict


class IconLoader:
    """Loads and caches icons as PhotoImage objects."""
    
    def __init__(self, icon_dir: str = None):
        """
        Initialize icon loader.
        
        Args:
            icon_dir: Directory containing icon files (default: icons/ in project root)
        """
        if icon_dir is None:
            # Get directory of this file and go to icons/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_dir = os.path.join(current_dir, 'icons')
        self.icon_dir = icon_dir
        self._cache: Dict[str, tk.PhotoImage] = {}
    
    def _svg_to_image(self, svg_path: str, size: tuple = (24, 24)) -> Optional[Image.Image]:
        """
        Convert SVG to PIL Image.
        
        Args:
            svg_path: Path to SVG file
            size: Target size (width, height)
            
        Returns:
            PIL Image or None if conversion fails
        """
        try:
            # Try using cairosvg if available
            import cairosvg
            png_data = cairosvg.svg2png(url=svg_path, output_width=size[0], output_height=size[1])
            return Image.open(BytesIO(png_data))
        except ImportError:
            # Fallback: try svglib
            try:
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPM
                drawing = svg2rlg(svg_path)
                if drawing:
                    img_data = renderPM.drawToString(drawing, fmt='PNG', dpi=72)
                    img = Image.open(BytesIO(img_data))
                    return img.resize(size, Image.Resampling.LANCZOS)
            except ImportError:
                pass
        
        # If all else fails, return None
        return None
    
    def load_icon(self, icon_name: str, size: tuple = (24, 24), color: str = 'white') -> Optional[tk.PhotoImage]:
        """
        Load an icon by name.
        
        Args:
            icon_name: Name of icon file (without extension, e.g., 'search')
            size: Size tuple (width, height)
            color: Color to use for fill (for SVG)
            
        Returns:
            PhotoImage object or None if loading fails
        """
        cache_key = f"{icon_name}_{size[0]}_{size[1]}_{color}"
        
        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try PNG first (most compatible)
        png_path = os.path.join(self.icon_dir, f"{icon_name}.png")
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path)
                if img.size != size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._cache[cache_key] = photo
                return photo
            except Exception as e:
                print(f"Error loading PNG icon {png_path}: {e}")
        
        # Try SVG as fallback
        svg_path = os.path.join(self.icon_dir, f"{icon_name}.svg")
        if os.path.exists(svg_path):
            # Read SVG and replace fill color if needed
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Replace fill="white" or fill="currentColor" with desired color
            if color != 'white':
                svg_content = svg_content.replace('fill="white"', f'fill="{color}"')
                svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')
            
            # Write temporary SVG with color
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as tmp:
                tmp.write(svg_content)
                tmp_path = tmp.name
            
            try:
                img = self._svg_to_image(tmp_path, size)
                if img:
                    photo = ImageTk.PhotoImage(img)
                    self._cache[cache_key] = photo
                    return photo
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        print(f"Warning: Icon '{icon_name}' not found in {self.icon_dir}")
        return None
    
    def get_icon_label(self, parent: tk.Widget, icon_name: str, size: tuple = (24, 24), 
                       bg: str = None, **kwargs) -> Optional[tk.Label]:
        """
        Create a Label widget with an icon.
        
        Args:
            parent: Parent widget
            icon_name: Name of icon
            size: Icon size
            bg: Background color for label
            **kwargs: Additional arguments for Label
            
        Returns:
            Label widget with icon or None if icon not found
        """
        icon = self.load_icon(icon_name, size)
        if icon:
            label = tk.Label(parent, image=icon, bg=bg, **kwargs)
            label.image = icon  # Keep a reference
            return label
        return None


# Global instance
_icon_loader: Optional[IconLoader] = None


def get_icon_loader() -> IconLoader:
    """Get or create global icon loader instance."""
    global _icon_loader
    if _icon_loader is None:
        _icon_loader = IconLoader()
    return _icon_loader


def load_icon(icon_name: str, size: tuple = (24, 24), color: str = 'white') -> Optional[tk.PhotoImage]:
    """Convenience function to load an icon."""
    return get_icon_loader().load_icon(icon_name, size, color)

