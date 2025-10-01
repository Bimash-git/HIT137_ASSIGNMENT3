from __future__ import annotations
from pathlib import Path
from typing import Any
import json

class SaveLoadMixin:
    """Mixin class that adds file saving capability to any class."""
    
    def save_output(self, content: Any, path: str | Path) -> Path:
        """Save content to a file. Auto-formats JSON for dicts/lists, plain text for others."""
        
        # Convert path to Path object for consistent file handling
        p = Path(path)
        
        # Check if content is dict or list → save as formatted JSON
        if isinstance(content, (dict, list)):
            # Serialize to JSON with 2-space indentation for readability
            p.write_text(json.dumps(content, indent=2), encoding="utf-8")
        else:
            # Convert any other type to string and save as plain text
            p.write_text(str(content), encoding="utf-8")
        
        # Return the Path object for confirmation or further use
        return p