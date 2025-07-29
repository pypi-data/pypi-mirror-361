"""
savekit - A lightweight JSON-based key-value storage toolkit.

Usage:
    from savekit import SaveKit

    db = SaveKit()
    db.put("user", "Pepe")
    print(db.get("user"))
"""

from .core import SaveKit

__all__ = ["SaveKit"]
__version__ = "1.1.0"
