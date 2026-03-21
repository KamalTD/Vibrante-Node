import hashlib
from src.utils.qt_compat import QtGui
QColor = QtGui.QColor

class ColorManager:
    _category_colors = {}
    
    # Pre-defined pleasant colors for common categories
    _defaults = {
        "Math": "#4A90E2",      # Blue
        "String": "#50fa7b",    # Green
        "Logic": "#ff79c6",     # Pink
        "IO": "#f1fa8c",        # Yellow
        "Data": "#bd93f9",      # Purple
        "Utility": "#8be9fd",   # Cyan
        "Control": "#ffb86c",   # Orange
        "Selection": "#ff5555"  # Red
    }

    @classmethod
    def get_category_color(cls, category: str) -> QColor:
        category = category.strip() or "General"
        
        if category in cls._defaults:
            return QColor(cls._defaults[category])
            
        if category in cls._category_colors:
            return cls._category_colors[category]
            
        # Generate a unique color based on the category name hash
        # We use HSL to ensure the colors are bright and distinct
        hash_object = hashlib.md5(category.encode())
        hash_hex = hash_object.hexdigest()
        
        # Use first few chars for hue (0-360)
        hue = int(hash_hex[:4], 16) % 360
        # Saturation 60-80%, Lightness 40-60% for good contrast/visibility
        color = QColor.fromHsl(hue, 180, 130) 
        
        cls._category_colors[category] = color
        return color

    @classmethod
    def get_all_categories(cls, registry_definitions):
        """Returns a list of unique categories found in the registry."""
        categories = set(cls._defaults.keys())
        for defn in registry_definitions.values():
            if defn.category:
                categories.add(defn.category)
        return sorted(list(categories))
